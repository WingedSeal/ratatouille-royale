import math
from queue import Queue
from random import shuffle
from typing import Iterator

from ratroyale.backend.entity_effect import EntityEffect

from .entities.rodent import Rodent
from .game_event import EntityMoveEvent, GameEvent
from .error import InvalidMoveTargetError, NotEnoughCrumbError
from .entity import Entity, SkillResult
from .hexagon import OddRCoord
from .player_info.player_info import PlayerInfo
from .player_info.squeak import Squeak
from .map import Map
from .board import Board
from .side import Side

HAND_LENGTH = 5


def crumb_per_turn(turn_count: int):
    return min(math.ceil(turn_count / 4) * 10, 50)


class GameManager:
    """
    Class responsible for main game logic, such as whose turn it is,
    how many crumbs each player has, etc.
    This class is not responsible for understand player input etc.
    """

    turn: Side
    """Whose turn it currently is"""
    turn_count: int
    """How many turns it has been"""
    board: Board
    """Game board"""
    hands: dict[Side, list[Squeak]]
    """Player's hand. Always have length of {HAND_LENGTH}"""
    players_info: dict[Side, PlayerInfo]
    decks: dict[Side, list[Squeak]]
    crumbs: int
    """Crumbs of the current side"""
    first_turn: Side

    def __init__(self, map: Map, players_info: tuple[PlayerInfo, PlayerInfo], first_turn: Side) -> None:
        self.turn = first_turn
        self.turn_count = 1
        self.board = Board(map)
        self.hands = {
            Side.RAT: [self.draw_squeak(Side.RAT) for _ in range(HAND_LENGTH)],
            Side.MOUSE: [self.draw_squeak(Side.MOUSE) for _ in range(HAND_LENGTH)],
        }
        self.players_info = {
            first_turn: players_info[0],
            first_turn.other_side(): players_info[1]
        }
        self.decks = {
            Side.RAT: self.players_info[Side.RAT].squeak_set.deck.copy(),
            Side.MOUSE: self.players_info[Side.MOUSE].squeak_set.deck.copy()
        }

    @property
    def event_queue(self) -> Queue[GameEvent]:
        return self.board.event_queue

    def activate_skill(self, entity: Entity, skill_index: int) -> SkillResult | None:
        skill = entity.skills[skill_index]
        if self.crumbs < skill.crumb_cost:
            raise NotEnoughCrumbError()
        self.crumbs -= skill.crumb_cost
        return skill.func(self)

    def get_enemy_on_pos(self, pos: OddRCoord) -> Entity:
        """
        Get enemy at the end of the list (top) at position. Raise error if there's nothing there
        """
        tile = self.board.get_tile(pos)
        if tile is None:
            raise ValueError("There is no tile on the coord")
        for entity in reversed(tile.entities):
            if entity.health is None:
                continue
            if entity.side == self.turn:
                continue
            return entity
        raise ValueError(f"No valid target on this pos ({pos})")

    def move_rodent(self, rodent: Rodent, target: OddRCoord) -> list[OddRCoord]:
        """
        Move rodent to target. Raise error if it cannot move there
        :param rodent: Rodent to move
        :param target: Target to move to
        :returns: Path the rodent took to get there
        """
        if self.crumbs < rodent.move_cost:
            raise NotEnoughCrumbError()
        if rodent.stamina <= 0:
            raise ValueError("Rodent doesn't have stamina left")
        if rodent.pos.get_distance(target) > rodent.speed:
            raise InvalidMoveTargetError("Cannot move rodent beyond its reach")
        path = self.board.path_find(rodent, target)
        if path is None:
            raise InvalidMoveTargetError()
        is_success = self.board.try_move(rodent, target)
        if not is_success:
            raise InvalidMoveTargetError("Cannot move rodent there")
        self.crumbs -= rodent.move_cost
        rodent.stamina -= 1
        self.event_queue.put(EntityMoveEvent(path, rodent))
        return path

    def move_entity_uncheck(self, entity: Entity, target: OddRCoord) -> list[OddRCoord]:
        """
        Blindly move entity to target. Neither crumbs nor speed was taken into account. But it still considers jump height.
        Raise error if it cannot move there
        :param entity: Entity to move
        :param target: Target to move to
        :returns: Path the rodent took to get there
        """
        path = self.board.path_find(entity, target)
        if path is None:
            raise InvalidMoveTargetError()
        is_success = self.board.try_move(entity, target)
        if not is_success:
            raise InvalidMoveTargetError("Cannot move entity there")
        self.event_queue.put(EntityMoveEvent(path, entity))
        return path

    def get_enemies_on_pos(self, pos: OddRCoord) -> Iterator[Entity]:
        """
        Get every damagable enemies at position. Raise error if there's nothing there
        """
        tile = self.board.get_tile(pos)
        if tile is None:
            raise ValueError("There is no tile on the coord")
        for entity in reversed(tile.entities):
            if entity.health is None:
                continue
            if entity.side == self.turn:
                continue
            yield entity

    def draw_squeak(self, side: Side) -> Squeak:
        """
        Get a squeak from a deck, spawn a new deck if it's empty
        """
        if self.decks[side]:
            return self.decks[side].pop()
        self.decks[side] = self.players_info[side].squeak_set.deck.copy()
        shuffle(self.decks[side])
        return self.decks[side].pop()

    def place_squeak(self, hand_index: int, coord: OddRCoord) -> bool:
        """
        Place squeak based on hand_index on the board
        """
        squeak = self.hands[self.turn][hand_index]
        if self.crumbs < squeak.crumb_cost:
            raise NotEnoughCrumbError()
        success = squeak.on_place(self.board, coord)
        if not success:
            return False
        self.crumbs -= squeak.crumb_cost
        self.hands[self.turn][hand_index] = self.draw_squeak(self.turn)
        return True

    def end_turn(self):
        for effect in self.board.cache.effects:
            effect.on_turn_change(self)
            if effect.duration == 1 and effect._should_clear(self.turn):
                active_effect = effect.entity.effects[effect.name]
                if active_effect != effect:
                    active_effect.overriden_effects.remove(effect)
                else:
                    self.effect_duration_over(effect)
        self.turn = self.turn.other_side()
        if self.turn == self.first_turn:
            for effect in self.board.cache.effects:
                if effect.duration is not None:
                    effect.duration -= 1
            self.turn_count += 1
        self.crumbs = crumb_per_turn(self.turn_count)

    def apply_effect(self, entity: Entity, effect: EntityEffect):
        old_effect = entity.effects.get(effect.name)
        if old_effect is None:
            entity.effects[effect.name] = effect
            self.board.cache.effects.append(effect)
            effect.on_applied(self, is_overriding=False)
            return
        if effect.intensity > old_effect.intensity:
            effect.overriden_effects.append(old_effect)
            self.board.cache.effects.append(effect)
            effect.on_applied(self, is_overriding=True)
            old_effect.on_cleared(self, is_overriden=True)
            return
        elif effect.intensity == old_effect.intensity:
            if old_effect.duration is None:
                return
            if effect.duration is not None and effect.duration <= old_effect.duration:
                return
            old_effect.duration = effect.duration
            return
        elif effect.intensity < old_effect.intensity:
            if old_effect.duration is None:
                return
            if effect.duration is not None and effect.duration <= old_effect.duration:
                return
            old_effect.overriden_effects.append(effect)
            self.board.cache.effects.append(effect)

    def effect_duration_over(self, effect: EntityEffect):
        self.board.cache.effects.remove(effect)
        if not effect.overriden_effects:
            effect.on_cleared(self, is_overriden=False)
            del effect.entity.effects[effect.name]
        effect.entity.effects = {
            name: e for name, e in effect.entity.effects.items() if (e.duration is None) or (e.duration > 1)}
        new_effect = max(effect.overriden_effects, key=lambda e: e.intensity)
        new_effect.on_applied(self, is_overriding=True)
        effect.on_cleared(self, is_overriden=True)
        effect.overriden_effects.remove(new_effect)
        new_effect.overriden_effects = effect.overriden_effects
        effect.entity.effects[effect.name] = new_effect

    def force_clear_effect(self, effect: EntityEffect):
        self.board.cache.effects.remove(effect)
        del effect.entity.effects[effect.name]
        for _effect in effect.overriden_effects:
            self.board.cache.effects.remove(_effect)
