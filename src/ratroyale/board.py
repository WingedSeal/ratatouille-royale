from copy import deepcopy

from .entities.rodent import RODENT_JUMP_HEIGHT, Rodent
from .hexagon import OddRCoord
from .tile import Tile
from .map import Map


class Board:
    size_x: int
    size_y: int
    tiles: list[list[Tile]]

    def __init__(self, map: Map) -> None:
        self.tiles = deepcopy(map.tiles)
        self.size_y = len(map.tiles)
        self.size_x = len(map.tiles[0])

    def get_tile(self, coord: OddRCoord) -> Tile | None:
        if coord.x < 0 or coord.x >= self.size_x:
            return None
        if coord.y < 0 or coord.y >= self.size_y:
            return None
        return self.tiles[coord.y][coord.x]

    def try_move(self, start: OddRCoord, end: OddRCoord) -> bool:
        """
        Check collision and move an entity from 1 tile to another.
        Not responsible for handling reach.

        :param start: Start coordinate. If there's no entity here, the function will fail.
        :param end: Target coordinate. If there's already an entity, the function will fail.
        :returns: Whether the move succeeded
        """
        start_tile = self.get_tile(start)
        end_tile = self.get_tile(end)
        if start_tile is None:
            return False
        if end_tile is None:
            return False
        for entity in reversed(start_tile.entities):
            if entity.movable:
                start_entity = entity
                break
        else:
            return False
        if start_entity.collision and any(entity.collision for entity in end_tile.entities):
            return False
        end_tile.entities.append(start_entity)
        start_tile.entities.remove(start_entity)
        start_entity.pos = end
        return True

    def get_reachable_tiles(self, rodent: Rodent, *, is_include_self: bool = False) -> set[OddRCoord]:
        def is_coord_blocked(coord: OddRCoord, previous_coord: OddRCoord):
            tile = self.get_tile(coord)
            if tile is None:
                return False
            previous_tile = self.get_tile(previous_coord)
            if previous_tile is None:
                return False
            return tile.get_total_height() - previous_tile.get_total_height() <= RODENT_JUMP_HEIGHT
        return rodent.pos.get_reachable_coords(
            rodent.speed, is_coord_blocked, is_include_self=is_include_self)
