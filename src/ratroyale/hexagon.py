class OddRCoord:
    """
    Odd-Row Coordinate for pointy-top hexagon tile. Top left is (0, 0),
    https://www.redblobgames.com/grids/hexagons/#coordinates-offset
    """

    x: int
    y: int

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
