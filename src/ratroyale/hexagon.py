from dataclasses import dataclass


@dataclass(frozen=True)
class OddRCoord:
    """
    Odd-Row Coordinate for pointy-top hexagon tile. Top left is (0, 0),
    https://www.redblobgames.com/grids/hexagons/#coordinates-offset
    """

    x: int
    y: int
