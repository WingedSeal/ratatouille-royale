import math
from random import shuffle
from typing import Iterator

from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.utils import EventQueue

from .board import Board
from .entities.rodent import Rodent
from .entity import Entity, SkillCompleted, SkillResult, SkillTargeting
from .entity_effect import EntityEffect
from .error import (
    GameManagerActionPerformedInSelectingMode,
    GameManagerSkillCallBackInNonSelectingMode,
    InvalidMoveTargetError,
    NotEnoughCrumbError,
    NotEnoughMoveStaminaError,
    NotEnoughSkillStaminaError,
)
from .feature import Feature
from .game_event import (
    EndTurnEvent,
    EntityEffectUpdateEvent,
    EntityMoveEvent,
    GameEvent,
)
from .hexagon import OddRCoord
from .map import Map
from .player_info.player_info import PlayerInfo
from .player_info.squeak import Squeak
from .side import Side

HAND_LENGTH = 5


def crumb_per_turn(turn_count: int) -> int:
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

    def __init__(
        self,
        map: Map,
        players_info: tuple[PlayerInfo, PlayerInfo],
        first_turn: Side,
    ) -> None:
        self.turn = first_turn
        self.first_turn = first_turn
        self.crumbs = 0
        self.turn_count = 1
        self.board = Board(map)
        self.players_info = {
            first_turn: players_info[0],
            first_turn.other_side(): players_info[1],
        }
        self.decks: dict[Side, list[Squeak]] = {}
        self.hands: dict[Side, list[Squeak]] = {}
        for side in Side:
            decks, hands = self.players_info[side].get_squeak_set().get_deck_and_hand()
            self.decks[side] = decks
            self.hands[side] = hands
        self.skill_targeting: SkillTargeting | None = None
        """
        If it is currently in selecting target mode. It'll have the detail of skill targeting.
        """

    @property
    def is_selecting_target(self) -> bool:
        return self.skill_targeting is not None

    @property
    def cancel_selecting_target(self) -> None:
        self.skill_targeting = None

    def _validate_not_selecting_target(self) -> None:
        if self.is_selecting_target:
            raise GameManagerActionPerformedInSelectingMode()

    @property
    def event_queue(self) -> EventQueue[GameEvent]:
        return self.board.event_queue

    def apply_skill_callback(
        self, selected_targets: list["OddRCoord"]
    ) -> "SkillResult":
        if self.skill_targeting is None:
            raise GameManagerSkillCallBackInNonSelectingMode()
        skill_result = self.skill_targeting._callback(self, selected_targets)
        if skill_result == SkillCompleted.SUCCESS:
            self.crumbs -= self.skill_targeting.source_skill.crumb_cost
            if self.skill_targeting.source_enitity.skill_stamina is not None:
                self.skill_targeting.source_enitity.skill_stamina -= 1
        if isinstance(skill_result, SkillTargeting):
            self.skill_targeting = skill_result
        else:
            self.skill_targeting = None
        return skill_result

    def activate_skill(self, entity: Entity, skill_index: int) -> SkillResult:
        """
        The result may either be a completed skill or require more targeting.

        .. example::
        ```python
        # Activate Skill
        skill_result = game_manager.activate_skill(self, entity, 1)
        ```
        ```python
        # Main Loop
        if self.game_manager.skill_targeting:
            ...
            selected_targets = ...
            if selected_targets is not None:
                skill_result = self.game_manager.apply_skill_callback(game_manager, selected_targets)
        ```
        """
        self._validate_not_selecting_target()
        skill = entity.skills[skill_index]
        if self.crumbs < skill.crumb_cost:
            raise NotEnoughCrumbError()
        if entity.skill_stamina is not None and entity.skill_stamina <= 0:
            raise NotEnoughSkillStaminaError()
        skill_result = skill.func(entity, self)
        if skill_result == SkillCompleted.SUCCESS:
            self.crumbs -= skill.crumb_cost
            if entity.skill_stamina is not None:
                entity.skill_stamina -= 1
        if isinstance(skill_result, SkillTargeting):
            if not skill_result.available_targets:
                return SkillCompleted.CANCELLED
            self.skill_targeting = skill_result
        return skill_result

    def get_enemy_on_pos(self, pos: OddRCoord) -> Entity | None:
        """
        Get enemy at the end of the list (top) at position or None if there's nothing there
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
        return None

    def get_ally_on_pos(self, pos: OddRCoord) -> Entity | None:
        """
        Get ally at the end of the list (top) at position or None if there's nothing there
        """
        tile = self.board.get_tile(pos)
        if tile is None:
            raise ValueError("There is no tile on the coord")
        for entity in reversed(tile.entities):
            if entity.health is None:
                continue
            if entity.side != self.turn:
                continue
            return entity
        return None

    def get_feature_on_pos(self, pos: OddRCoord) -> Feature | None:
        """
        Get feature at the end of the list (top) at position or None if there's nothing there
        """
        tile = self.board.get_tile(pos)
        if tile is None:
            raise ValueError("There is no tile on the coord")
        for feature in reversed(tile.features):
            if feature.health is None:
                continue
            if feature.side == self.turn:
                continue
            return feature
        return None

    def move_rodent(
        self,
        rodent: Rodent,
        target: OddRCoord,
        custom_path: list[OddRCoord] | None = None,
    ) -> list[OddRCoord]:
        """
        Move rodent to target. Raise error if it cannot move there
        :param rodent: Rodent to move
        :param target: Target to move to
        :param custom_path: Force rodent to move in a specific path if not None, defaults to `None`
        :returns: Path the rodent took to get there
        """
        self._validate_not_selecting_target()
        if self.crumbs < rodent.move_cost:
            raise NotEnoughCrumbError()
        if rodent.move_stamina <= 0:
            raise NotEnoughMoveStaminaError()
        if rodent.pos.get_distance(target) > rodent.speed:
            raise InvalidMoveTargetError("Cannot move rodent beyond its reach")
        if custom_path is not None:
            raise NotImplementedError("Custom pathing isn't implemented yet")
        path = self.board.path_find(rodent, target)
        if path is None:
            raise InvalidMoveTargetError()
        is_success = self.board.try_move(rodent, target)
        if not is_success:
            raise InvalidMoveTargetError("Cannot move rodent there")
        self.crumbs -= rodent.move_cost
        rodent.move_stamina -= 1
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
        self._validate_not_selecting_target()
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

    def _draw_squeak(self, side: Side) -> Squeak:
        """
        Get a squeak from a deck, spawn a new deck if it's empty
        """
        if self.decks[side]:
            return self.decks[side].pop()
        self.decks[side] = self.players_info[side].get_squeak_set().get_new_deck()
        shuffle(self.decks[side])
        return self.decks[side].pop()

    def place_squeak(self, hand_index: int, coord: OddRCoord) -> None:
        """
        Place squeak based on hand_index on the board
        """
        squeak = self.hands[self.turn][hand_index]
        if self.crumbs < squeak.crumb_cost:
            raise NotEnoughCrumbError()
        squeak.on_place(self, coord)
        self.crumbs -= squeak.crumb_cost
        self.hands[self.turn][hand_index] = self._draw_squeak(self.turn)

    def end_turn(self) -> None:
        self._validate_not_selecting_target()
        for effect in self.board.cache.effects:
            effect.on_turn_change(self)
            if effect.duration == 1 and effect._should_clear(self.turn):
                active_effect = effect.entity.effects[effect.name]
                if active_effect != effect:
                    active_effect.overridden_effects.remove(effect)
                else:
                    self.effect_duration_over(effect)
        from_side = self.turn
        self.turn = self.turn.other_side()
        if self.turn == self.first_turn:
            for effect in self.board.cache.effects:
                if effect.duration is not None:
                    effect.duration -= 1
            self.turn_count += 1
        leftover_crumbs = self.crumbs
        self.crumbs = crumb_per_turn(self.turn_count)
        self.event_queue.put_nowait(
            EndTurnEvent(
                from_side=from_side,
                to_side=self.turn,
                leftover_crumbs=leftover_crumbs,
                new_crumbs=self.crumbs,
            )
        )

    def apply_effect(self, entity: Entity, effect: EntityEffect) -> None:
        old_effect = entity.effects.get(effect.name)
        if old_effect is None:
            entity.effects[effect.name] = effect
            self.board.cache.effects.append(effect)
            effect.on_applied(self, is_overriding=False)
            self.event_queue.put_nowait(
                EntityEffectUpdateEvent(effect, "apply", "normal_apply")
            )
            return
        if effect.intensity > old_effect.intensity:
            effect.overridden_effects.append(old_effect)
            self.board.cache.effects.append(effect)
            effect.on_applied(self, is_overriding=True)
            self.event_queue.put_nowait(
                EntityEffectUpdateEvent(effect, "apply", "overriding")
            )
            old_effect.on_cleared(self, is_overridden=True)
            self.event_queue.put_nowait(
                EntityEffectUpdateEvent(effect, "clear", "overriden")
            )
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
            old_effect.overridden_effects.append(effect)
            self.board.cache.effects.append(effect)

    def effect_duration_over(self, effect: EntityEffect) -> None:
        self.board.cache.effects.remove(effect)
        if not effect.overridden_effects:
            effect.on_cleared(self, is_overridden=False)
            self.event_queue.put_nowait(
                EntityEffectUpdateEvent(effect, "clear", "duration_over")
            )
            del effect.entity.effects[effect.name]
        effect.entity.effects = {
            name: e
            for name, e in effect.entity.effects.items()
            if (e.duration is None) or (e.duration > 1)
        }
        new_effect = max(effect.overridden_effects, key=lambda e: e.intensity)
        new_effect.on_applied(self, is_overriding=True)
        self.event_queue.put_nowait(
            EntityEffectUpdateEvent(
                effect, "apply", "replacing_stronger_effect_that_duration_over"
            )
        )
        effect.on_cleared(self, is_overridden=True)
        self.event_queue.put_nowait(
            EntityEffectUpdateEvent(
                effect, "clear", "duration_over_and_replaced_by_weaker_effect"
            )
        )
        effect.overridden_effects.remove(new_effect)
        new_effect.overridden_effects = effect.overridden_effects
        effect.entity.effects[effect.name] = new_effect

    def force_clear_effect(self, effect: EntityEffect) -> None:
        self.board.cache.effects.remove(effect)
        del effect.entity.effects[effect.name]
        for _effect in effect.overridden_effects:
            self.board.cache.effects.remove(_effect)
        effect.on_cleared(self, is_overridden=False)
        self.event_queue.put_nowait(
            EntityEffectUpdateEvent(effect, "clear", "force_clear")
        )
