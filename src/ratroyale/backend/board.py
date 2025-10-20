from collections import defaultdict
from copy import deepcopy
from typing import Iterable, Iterator

from ..utils import EventQueue, is_ellipsis_body
from .entities.rodent import ENTITY_JUMP_HEIGHT, Rodent
from .entity import CallableEntitySkill, Entity
from .entity_effect import EntityEffect
from .error import EntityInvalidPosError
from .feature import Feature
from .features.common import DeploymentZone, Lair
from .game_event import EntitySpawnEvent, GameEvent
from .hexagon import IsCoordBlocked, OddRCoord
from .map import Map
from .side import Side
from .tile import Tile
from .timer import Timer


class Cache:
    def __init__(self) -> None:
        self.rodents: list[Rodent] = []
        self.sides: dict[Side | None, list[Entity]] = defaultdict(list)
        self.entities: list[Entity] = []
        self.entities_with_hp: list[Entity] = []
        self.sides_with_hp: dict[Side | None, list[Entity]] = defaultdict(list)
        self.features: list[Feature] = []
        self.deployment_zones: dict[Side | None, list[DeploymentZone]] = defaultdict(
            list
        )
        self.lairs: dict[Side, list[Lair]] = defaultdict(list)
        self.effects: list[EntityEffect] = []
        self.timers: list[Timer] = []
        self.entities_with_turn_change: list[Entity] = []
        self.entities_in_features: dict[Entity, list[Feature]] = defaultdict(list)

    def get_all_lairs(self) -> Iterable[Lair]:
        for side_lair in self.lairs.values():
            for lair in side_lair:
                yield lair


class Board:
    size_x: int
    size_y: int
    tiles: list[list[Tile | None]]
    cache: Cache
    event_queue: EventQueue[GameEvent]

    def __init__(self, map: Map) -> None:
        self.cache = Cache()
        map = deepcopy(map)
        self.tiles = map.tiles
        self.cache.features = map.features
        for feature in self.cache.features:
            if isinstance(feature, DeploymentZone):
                self.cache.deployment_zones[feature.side].append(feature)
            elif isinstance(feature, Lair):
                if feature.side is None:
                    raise ValueError("Lair cannot have side of None")
                self.cache.lairs[feature.side].append(feature)
        self.size_y = len(map.tiles)
        self.size_x = len(map.tiles[0])
        self.event_queue = EventQueue()
        for entity in map.entities:
            self.add_entity(entity)

    def add_entity(self, entity: Entity) -> None:
        self.cache.entities.append(entity)
        self.cache.sides[entity.side].append(entity)
        if entity.health is not None:
            self.cache.entities_with_hp.append(entity)
            self.cache.sides_with_hp[entity.side].append(entity)
        if isinstance(entity, Rodent):
            self.cache.rodents.append(entity)
        if not is_ellipsis_body(entity.on_turn_change):
            self.cache.entities_with_turn_change.append(entity)
        tile = self.get_tile(entity.pos)
        if tile is None:
            raise EntityInvalidPosError()
        tile.entities.append(entity)
        self.event_queue.put_nowait(EntitySpawnEvent(entity))

    def remove_entity(self, entity: Entity) -> None:
        """Remove entity from cache"""
        self.cache.entities.remove(entity)
        self.cache.sides[entity.side].remove(entity)
        if entity in self.cache.entities_in_features:
            del self.cache.entities_in_features[entity]
        if entity.health is not None:
            self.cache.entities_with_hp.remove(entity)
            self.cache.sides_with_hp[entity.side].remove(entity)
        if isinstance(entity, Rodent):
            self.cache.rodents.remove(entity)
        if not is_ellipsis_body(entity.on_turn_change):
            self.cache.entities_with_turn_change.remove(entity)

    def get_tile(self, coord: OddRCoord) -> Tile | None:
        if coord.x < 0 or coord.x >= self.size_x:
            return None
        if coord.y < 0 or coord.y >= self.size_y:
            return None
        return self.tiles[coord.y][coord.x]

    def is_coord_blocked(
        self, entity: Entity, custom_jump_height: int | None = None
    ) -> IsCoordBlocked:
        return self._is_coord_blocked(entity.collision, entity.side, custom_jump_height)

    def _is_coord_blocked(
        self, collision: bool, side: Side | None, custom_jump_height: int | None = None
    ) -> IsCoordBlocked:
        if custom_jump_height is None:
            custom_jump_height = ENTITY_JUMP_HEIGHT

        def is_coord_blocked(target_coord: OddRCoord, source_coord: OddRCoord) -> bool:
            target_tile = self.get_tile(target_coord)
            if target_tile is None:
                return True
            if collision and any(_entity.collision for _entity in target_tile.entities):
                return True
            if any(feature.is_collision() for feature in target_tile.features):
                return True
            previous_tile = self.get_tile(source_coord)
            if previous_tile is None:
                return True
            return (
                target_tile.get_total_height(side)
                - previous_tile.get_total_height(side)
                > custom_jump_height
            )

        return is_coord_blocked

    def line_of_sight_check(
        self,
        start_coord: OddRCoord,
        end_coord: OddRCoord,
        altitude: int,
        turn: Side | None,
        max_range: int | None = None,
    ) -> bool:
        if max_range is not None and start_coord.get_distance(end_coord) > max_range:
            return False
        start_tile = self.get_tile(start_coord)
        if start_tile is None:
            raise ValueError("Start tile has invalid pos")
        start_height = start_tile.get_total_height(turn)
        for coord in start_coord.line_draw(end_coord):
            tile = self.get_tile(coord)
            if tile is None:
                return False
            if tile.get_total_height(turn) + altitude < start_height:
                return False
        return True

    def try_move(self, entity: Entity, path: list[OddRCoord]) -> bool:
        """
        Check collision and move an entity from 1 tile to another.
        Not responsible for handling reach.
        Does not trigger EntityMoveEvent.

        :param entity: Entity to move
        :param path: Path coordinates. If there's already an entity, the function will fail.
        :returns: Whether the move succeeded
        """
        start_coord = entity.pos
        start_tile = self.get_tile(start_coord)
        if start_tile is None:
            raise EntityInvalidPosError()
        path_tile = None
        for path_coord in path:
            path_tile = self.get_tile(path_coord)
            if path_tile is None:
                return False
            if path_tile.is_collision(entity.collision):
                return False
        end_tile = path_tile
        assert end_tile is not None
        end_tile.entities.append(entity)
        start_tile.entities.remove(entity)
        entity.pos = path[-1]

        return True

    def get_reachable_coords(
        self, rodent: Rodent, *, is_include_self: bool = False
    ) -> set[OddRCoord]:
        """
        Get every coords a rodent can reach within its movement limit

        :param rodent: The rodent
        :param is_include_self: Whether to include the coord of rodent itself in the result
        :returns: Set of reachable coords
        """
        return rodent.pos.get_reachable_coords(
            rodent.speed,
            self.is_coord_blocked(rodent),
            is_include_self=is_include_self,
        )

    def path_find(
        self, entity: Entity, goal: OddRCoord, custom_jump_height: int | None = None
    ) -> list[OddRCoord] | None:
        return entity.pos.path_find(
            goal, self.is_coord_blocked(entity, custom_jump_height)
        )

    def get_attackable_coords(
        self, rodent: Rodent, skill: CallableEntitySkill
    ) -> Iterator[OddRCoord]:
        """
        Get every coords a rodent can attack with its skill altitude

        :param rodent: The rodent
        :param skill: Which skills of the rodent to use in calculation
        :returns: All attackable coords
        """
        rodent_tile = self.get_tile(rodent.pos)
        if rodent_tile is None:
            raise ValueError("Rodent has invalid pos")
        max_altitude = rodent_tile.get_total_height(rodent.side) + (skill.altitude or 0)
        reach = skill.reach
        if reach is None:
            raise ValueError("'get_attackable_coords is called on skill without reach")
        for target_coord in rodent.pos.all_in_range(reach):
            for passed_coord in rodent.pos.line_draw(target_coord):
                passed_tile = self.get_tile(passed_coord)
                if passed_tile is None:
                    break
                if passed_tile.get_total_height(rodent.side) > max_altitude:
                    break
            else:
                yield target_coord
