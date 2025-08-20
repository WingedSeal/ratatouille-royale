from dataclasses import dataclass
from typing import Self
from .utils import lerp


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

    def get_distance(self, other: Self) -> int:
        return self.to_cube().get_distance(other.to_cube())

    def __sub__(self, other: Self) -> Self:
        return self.__class__(self.x - other.x, self.y - other.y)


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

    def __sub__(self, other: Self) -> Self:
        return self.__class__(self.q - other.q, self.r - other.r)


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

    def get_distance(self, other: Self) -> int:
        """
        https://www.redblobgames.com/grids/hexagons/#distances-cube
        """
        vec = self - other
        return (abs(vec.q) + abs(vec.r) + abs(vec.s)) // 2

    def __sub__(self, other: Self) -> Self:
        return self.__class__(self.q - other.q, self.r - other.r, self.s - other.s)

    def to_float(self) -> "_CubeCoordFloat":
        return _CubeCoordFloat(self.q, self.r, self.s)


@dataclass(frozen=True)
class _CubeCoordFloat:
    q: float
    r: float
    s: float

    def round(self) -> "_CubeCoord":
        q = round(self.q)
        r = round(self.r)
        s = round(self.s)

        q_diff = abs(q - self.q)
        r_diff = abs(r - self.r)
        s_diff = abs(s - self.s)

        if q_diff > r_diff and q_diff > s_diff:
            q = -r-s
        elif r_diff > s_diff:
            r = -q-s
        else:
            s = -q-r

        return _CubeCoord(q, r, s)

    def lerp(self, other: "_CubeCoordFloat", t: float) -> "_CubeCoordFloat":
        return _CubeCoordFloat(
            lerp(self.q, other.q, t),
            lerp(self.r, other.r, t),
            lerp(self.s, other.s, t),
        )
