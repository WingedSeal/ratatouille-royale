from collections import defaultdict
from copy import deepcopy
from typing import Iterator

from .features.commmon import DeploymentZone, Lair
from .feature import Feature
from .entity_effect import EntityEffect
from ..utils import EventQueue
from .game_event import EntityDamagedEvent, EntitySpawnEvent, FeatureDamagedEvent, FeatureDieEvent, GameEvent, EntityDieEvent
from .error import EntityInvalidPosError
from .side import Side
from .entity import Entity, EntitySkill
from .entities.rodent import ENTITY_JUMP_HEIGHT, Rodent
from .hexagon import IsCoordBlocked, OddRCoord
from .tile import Tile
from .map import Map


class Cache:
    def __init__(self) -> None:
        self.rodents: list[Rodent] = []
        self.sides: dict[Side | None, list[Entity]] = defaultdict(list)
        self.entities: list[Entity] = []
        self.entities_with_hp: list[Entity] = []
        self.sides_with_hp: dict[Side | None, list[Entity]] = defaultdict(list)
        self.features: list[Feature] = []
        self.deployment_zones: dict[Side | None,
                                    list[DeploymentZone]] = defaultdict(list)
        self.lairs: dict[Side, list[Lair]] = defaultdict(list)
        self.effects: list[EntityEffect] = []


class Board:
    size_x: int
    size_y: int
    tiles: list[list[Tile | None]]
    cache: Cache
    event_queue: EventQueue[GameEvent]

    def __init__(self, map: Map) -> None:
        self.cache = Cache()
        self.tiles = deepcopy(map.tiles)
        self.cache.features = deepcopy(map.features)
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
        tile = self.get_tile(entity.pos)
        if tile is None:
            raise EntityInvalidPosError()
        tile.entities.append(entity)
        self.event_queue.put(EntitySpawnEvent(entity))

    def get_tile(self, coord: OddRCoord) -> Tile | None:
        if coord.x < 0 or coord.x >= self.size_x:
            return None
        if coord.y < 0 or coord.y >= self.size_y:
            return None
        return self.tiles[coord.y][coord.x]

    def _is_coord_blocked(self, entity: Entity) -> IsCoordBlocked:
        def is_coord_blocked(target_coord: OddRCoord, source_coord: OddRCoord) -> bool:
            target_tile = self.get_tile(target_coord)
            if target_tile is None:
                return True
            if entity.collision and any(_entity.collision for _entity in target_tile.entities):
                return True
            previous_tile = self.get_tile(source_coord)
            if previous_tile is None:
                return True
            return target_tile.get_total_height(entity.side) - previous_tile.get_total_height(entity.side) > ENTITY_JUMP_HEIGHT
        return is_coord_blocked

    def damage_entity(self, entity: Entity, damage: int):
        """
        Damage an entity. Doesn't work on entity with no health.
        """
        is_dead, damage_taken = entity._take_damage(damage)
        self.event_queue.put(EntityDamagedEvent(entity, damage, damage_taken))
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

    def damage_feature(self, feature: Feature, damage: int):
        """
        Damage a feature. Doesn't work on feature with no health.
        """
        is_dead, damage_taken = feature._take_damage(damage)
        self.event_queue.put(FeatureDamagedEvent(
            feature, damage, damage_taken))
        if not is_dead:
            return
        is_dead = feature.on_death()
        if not is_dead:
            return

        for pos in feature.shape:
            tile = self.get_tile(pos)
            if tile is None:
                raise ValueError("Feature is existing on invalid tile")
            tile.features.remove(feature)
        self.cache.features.remove(feature)
        if isinstance(feature, DeploymentZone):
            self.cache.deployment_zones[feature.side].remove(feature)
        elif isinstance(feature, Lair):
            if feature.side is None:
                raise ValueError("Lair cannot have side of None")
            self.cache.lairs[feature.side].remove(feature)
        self.event_queue.put(FeatureDieEvent(feature))

    def line_of_sight_check(self, start_coord: OddRCoord, end_coord: OddRCoord, altitude: int, turn: Side | None, max_range: int | None = None) -> bool:
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

    def try_move(self, entity: Entity, target: OddRCoord) -> bool:
        """
        Check collision and move an entity from 1 tile to another.
        Not responsible for handling reach.
        Does not trigger EntityMoveEvent.

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
        return True

    def get_reachable_coords(self, rodent: Rodent, *, is_include_self: bool = False) -> set[OddRCoord]:
        """
        Get every coords a rodent can reach within its movement limit

        :param rodent: The rodent
        :param is_include_self: Whether to include the coord of rodent itself in the result
        :returns: Set of reachable coords
        """
        return rodent.pos.get_reachable_coords(
            rodent.speed, self._is_coord_blocked(rodent), is_include_self=is_include_self)

    def path_find(self, entity: Entity, goal: OddRCoord):
        return entity.pos.path_find(goal, self._is_coord_blocked(entity))

    def get_attackable_coords(self, rodent: Rodent, skill: EntitySkill) -> Iterator[OddRCoord]:
        """
        Get every coords a rodent can attack with its skill altitude

        :param rodent: The rodent
        :param skill: Which skills of the rodent to use in calculation
        :returns: All attackable coords
        """
        rodent_tile = self.get_tile(rodent.pos)
        if rodent_tile is None:
            raise ValueError("Rodent has invalid pos")
        max_altitude = rodent_tile.get_total_height(rodent.side
                                                    ) + (skill.altitude or 0)
        reach = skill.reach
        if reach is None:
            raise ValueError(
                "'get_attackable_coords is called on skill without reach")
        for target_coord in rodent.pos.all_in_range(reach):
            for passed_coord in rodent.pos.line_draw(target_coord):
                passed_tile = self.get_tile(passed_coord)
                if passed_tile is None:
                    break
                if passed_tile.get_total_height(rodent.side) > max_altitude:
                    break
            else:
                yield target_coord
