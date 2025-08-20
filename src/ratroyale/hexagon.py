from dataclasses import dataclass
from typing import Iterator, Self
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

    def line_draw(self, other: "OddRCoord") -> Iterator["OddRCoord"]:
        return (cube.to_odd_r() for cube in self.to_cube().line_draw(other.to_cube()))

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

    def line_draw(self, other: Self) -> Iterator["_CubeCoord"]:
        """
        https://www.redblobgames.com/grids/hexagons/#line-drawing
        """
        N = self.get_distance(other)
        for i in range(N):
            yield self.to_cube_float(add_epsilon=(
                1e-6, 2e-6, -3e-6)).lerp(other.to_cube_float(), 1/N * i).round()

    def __sub__(self, other: Self) -> Self:
        return self.__class__(self.q - other.q, self.r - other.r, self.s - other.s)

    def to_cube_float(self, add_epsilon: tuple[float, float, float] | None = None) -> "_CubeCoordFloat":
        """
        There are times when cube_lerp will return a point that's exactly on
        the side between two hexes. Then cube_round will push it one way or the
        other. The lines will look better if it's always pushed in the same
        direction. You can do this by adding an "epsilon" hex Cube(1e-6, 2e-6,
        -3e-6) to one or both of the endpoints before starting the loop. This
        will "nudge" the line in one direction to avoid landing on side
        boundaries.

        https://www.redblobgames.com/grids/hexagons/#line-drawing
        """
        if add_epsilon is None:
            return _CubeCoordFloat(self.q, self.r, self.s)
        else:
            return _CubeCoordFloat(self.q + add_epsilon[0], self.r + add_epsilon[1], self.s + add_epsilon[2])


@dataclass(frozen=True)
class _CubeCoordFloat:
    q: float
    r: float
    s: float

    def round(self) -> "_CubeCoord":
        """
        https://www.redblobgames.com/grids/hexagons/#rounding
        """
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

    def lerp(self, other: Self, t: float) -> Self:
        """
        https://www.redblobgames.com/grids/hexagons/#line-drawing
        """
        return self.__class__(
            lerp(self.q, other.q, t),
            lerp(self.r, other.r, t),
            lerp(self.s, other.s, t),
        )
