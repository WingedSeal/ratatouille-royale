from dataclasses import dataclass


@dataclass(frozen=True)
class OddRCoord:
    """
    Odd-Row Coordinate for pointy-top hexagon tile. Top left is (0, 0),
    https://www.redblobgames.com/grids/hexagons/#coordinates-offset
    """
    x: int
    y: int

    @property
    def row(self):
        return self.y

    @property
    def col(self):
        return self.x

    def to_axial(self) -> "_AxialCoord":
        """
        https://www.redblobgames.com/grids/hexagons/#conversions-offset
        """
        parity = self.row & 1
        q = self.col - (self.row - parity) // 2
        r = self.row
        return _AxialCoord(q, r)

    def to_cube(self) -> "_CubeCoord":
        return self.to_axial().to_cube()


@dataclass(frozen=True)
class _AxialCoord:
    q: int
    r: int

    def to_cube(self) -> "_CubeCoord":
        """
        https://www.redblobgames.com/grids/hexagons/#conversions-axial
        """
        return _CubeCoord(self.q, self.r, -self.q-self.r)

    def to_odd_r(self) -> "OddRCoord":
        """
        https://www.redblobgames.com/grids/hexagons/#conversions-offset
        """
        parity = self.r & 1
        col = self.q + (self.r - parity) // 2
        row = self.r
        return OddRCoord(col, row)


@dataclass(frozen=True)
class _CubeCoord:
    q: int
    r: int
    s: int

    def to_axial(self) -> "_AxialCoord":
        """
        https://www.redblobgames.com/grids/hexagons/#conversions-axial
        """
        return _AxialCoord(self.q, self.r)

    def to_odd_r(self) -> "OddRCoord":
        return self.to_axial().to_odd_r()
