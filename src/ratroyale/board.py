from ratroyale.hexagon import OddRCoord
from .tile import Tile
from .map import Map


class Board:
    size_x: int
    size_y: int
    tiles: list[list[Tile]]

    def __init__(self, map: Map) -> None:
        pass

    def move_uncheck(self, start: OddRCoord, end: OddRCoord) -> None:
        pass

    def try_move(self, start: OddRCoord, end: OddRCoord) -> bool:
        """
        Check collision and move an entity from 1 tile to another.
        Not responsible for handling reach.

        :param start: Start coordinate. If there's no entity here, the function will fail.
        :param end: Target coordinate. If there's already an entity, the function will fail.
        :returns: Whether the move succeeded
        """
        return True
        pass
