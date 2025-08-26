from copy import deepcopy
from typing import Iterator

from ..utils import EventQueue
from .game_event import EntityMoveEvent, GameEvent, EntityDieEvent
from .error import EntityInvalidPosError
from .side import Side
from .entity import Entity
from .entities.rodent import RODENT_JUMP_HEIGHT, Rodent
from .hexagon import OddRCoord
from .tile import Tile
from .map import Map


class CachedEntities:
    def __init__(self) -> None:
        self.rodents: list[Rodent] = []
        self.rats: list[Rodent] = []
        self.mice: list[Rodent] = []
        self.entities: list[Entity] = []


class Board:
    size_x: int
    size_y: int
    tiles: list[list[Tile]]
    cached_entities: CachedEntities
    event_queue: EventQueue[GameEvent]

    def __init__(self, map: Map) -> None:
        self.tiles = deepcopy(map.tiles)
        self.size_y = len(map.tiles)
        self.size_x = len(map.tiles[0])
        self.cached_entities = CachedEntities()
        self.event_queue = EventQueue()
        for entity in map.entities:
            self.add_entity(entity)

    def add_entity(self, entity: Entity) -> None:
        self.cached_entities.entities.append(entity)
        if isinstance(entity, Rodent):
            self.cached_entities.rodents.append(entity)
            if entity.side == Side.RAT:
                self.cached_entities.rats.append(entity)
            elif entity.side == Side.MOUSE:
                self.cached_entities.mice.append(entity)
        tile = self.get_tile(entity.pos)
        if tile is None:
            raise EntityInvalidPosError()
        tile.entities.append(entity)

    def get_tile(self, coord: OddRCoord) -> Tile | None:
        if coord.x < 0 or coord.x >= self.size_x:
            return None
        if coord.y < 0 or coord.y >= self.size_y:
            return None
        return self.tiles[coord.y][coord.x]

    def damage_entity(self, entity: Entity, damage: int):
        is_dead = entity._take_damage(damage)
        if not is_dead:
            return
        is_dead = entity.on_death()
        if not is_dead:
            return
        tile = self.get_tile(entity.pos)
        if tile is None:
            raise EntityInvalidPosError()
        tile.entities.remove(entity)
        self.event_queue.put(EntityDieEvent(entity))

    def try_move(self, entity: Entity, target: OddRCoord) -> bool:
        """
        Check collision and move an entity from 1 tile to another.
        Not responsible for handling reach.

        :param entity: Entity to move
        :param end: Target coordinate. If there's already an entity, the function will fail.
        :returns: Whether the move succeeded
        """
        start_coord = entity.pos
        start_tile = self.get_tile(start_coord)
        if start_tile is None:
            raise EntityInvalidPosError()
        end_tile = self.get_tile(target)
        if end_tile is None:
            return False
        if entity.collision and any(_entity.collision for _entity in end_tile.entities):
            return False
        end_tile.entities.append(entity)
        start_tile.entities.remove(entity)
        entity.pos = target
        self.event_queue.put(EntityMoveEvent(start_coord, target, entity))
        return True

    def get_reachable_coords(self, rodent: Rodent, *, is_include_self: bool = False) -> set[OddRCoord]:
        """
        Get every coords a rodent can reach within its movement limit

        :param rodent: The rodent
        :param is_include_self: Whether to include the coord of rodent itself in the result
        :returns: Set of reachable coords
        """
        def is_coord_blocked(target_coord: OddRCoord, source_coord: OddRCoord) -> bool:
            tile = self.get_tile(target_coord)
            if tile is None:
                return False
            previous_tile = self.get_tile(source_coord)
            if previous_tile is None:
                return False
            return tile.get_total_height() - previous_tile.get_total_height() <= RODENT_JUMP_HEIGHT
        return rodent.pos.get_reachable_coords(
            rodent.speed, is_coord_blocked, is_include_self=is_include_self)

    def get_attackable_coords(self, rodent: Rodent, skill_index: int) -> Iterator[OddRCoord]:
        """
        Get every coords a rodent can attack with its skill altitude

        :param rodent: The rodent
        :param skill_index: Which skills of the rodent to use in calculation
        :returns: All attackable coords
        """
        rodent_tile = self.get_tile(rodent.pos)
        if rodent_tile is None:
            raise ValueError("Rodent has invalid pos")
        max_altitude = rodent_tile.get_total_height(
        ) + (rodent.skills[skill_index].altitude or 0)
        reach = rodent.skills[skill_index].reach
        if reach is None:
            raise ValueError(
                "'get_attackable_coords is called on skill without reach")
        for target_coord in rodent.pos.all_in_range(reach):
            for passed_coord in rodent.pos.line_draw(target_coord):
                passed_tile = self.get_tile(passed_coord)
                if passed_tile is None:
                    break
                if passed_tile.get_total_height() > max_altitude:
                    break
            else:
                yield target_coord
