from ..utils import lerp as lerp
from dataclasses import dataclass, field
from typing import Callable, Iterator, Protocol, Self, overload

class IsCoordBlocked(Protocol):
    """
    A callback function that evaluate whether target coord is accessible from source coord
    """

    def __call__(self, target_coord: OddRCoord, source_coord: OddRCoord) -> bool:
        """
        A callback function that evaluate whether target coord is accessible from source coord
        """
        ...

@dataclass(frozen=True)
class OddRCoord:
    """
    Odd-Row Coordinate for pointy-top hexagon tile. Top left is (0, 0),
    https://www.redblobgames.com/grids/hexagons/#coordinates-offset
    """

    x: int
    y: int
    @property
    def row(self) -> int: ...
    @property
    def col(self) -> int: ...
    def to_axial(self) -> _AxialCoord:
        """
        https://www.redblobgames.com/grids/hexagons/#conversions-offset
        """
        ...

    def to_cube(self) -> _CubeCoord: ...
    def get_distance(self, other: Self) -> int: ...
    def line_draw(self, other: Self) -> Iterator["OddRCoord"]: ...
    def all_in_range(self, N: int) -> Iterator["OddRCoord"]: ...
    @overload
    def to_pixel(
        self, hex_size: float, is_bounding_box: bool = False
    ) -> tuple[float, float]: ...
    @overload
    def to_pixel(
        self, hex_width: float, hex_height: float, is_bounding_box: bool = False
    ) -> tuple[float, float]:
        """
        https://www.redblobgames.com/grids/hexagons/#hex-to-pixel-offset
        https://www.redblobgames.com/grids/hexagons/#hex-to-pixel-mod-origin
        is_bounding_box: Whether hex_width and hex_height specify the hexagon's bounding box instead of its radius.
        """
        ...

    def get_neighbor(self, direction: int) -> OddRCoord:
        """
        Get neighbor on a specific direction
        :param direction: The direction to get the neighbor, ranges between 0 (top left) to 5 (left)
        :returns: Neighbor coord
        """
        ...

    def get_neighbors(self) -> Iterator["OddRCoord"]:
        """
        Get all 6 neighbors
        """
        ...

    def get_reachable_coords(
        self,
        reach: int,
        is_coord_blocked: IsCoordBlocked = ...,
        *,
        is_include_self: bool = False,
    ) -> set["OddRCoord"]:
        """
        Get every reachable coords within reach
        https://www.redblobgames.com/grids/hexagons/#range-obstacles

        :param reach: Movement from original coord
        :param is_coord_blocked: A callback function that evaluate whether target coord is accessible from source coord
        :returns: Reachable coords
        """
        ...

    @classmethod
    def from_pixel(cls, x: float, y: float, hex_size: float) -> OddRCoord: ...
    def __add__(self, other: Self) -> Self: ...
    def __sub__(self, other: Self) -> Self: ...
    def path_find(
        self,
        goal: OddRCoord,
        is_coord_blocked: IsCoordBlocked,
        get_cost: Callable[[OddRCoord, OddRCoord], float] = ...,
    ) -> list["OddRCoord"] | None:
        """
        https://www.redblobgames.com/pathfinding/a-star/introduction.html#astar

        Using A-star method to path find to a goal

        :param goal: Goal coord
        :param is_coord_blocked: A callback function that evaluate whether target coord is accessible from source coord
        :param get_cost: A callback function to evaluate cost to travel from first coord to second coord, defaults to `lambda: a, b: 1.0`
        :returns: Path calculated or None if goal is not reachable
        """
        ...

@dataclass(frozen=True)
class _AxialCoord:
    q: int
    r: int
    def to_cube(self) -> _CubeCoord:
        """
        https://www.redblobgames.com/grids/hexagons/#conversions-axial
        """
        ...

    def to_odd_r(self) -> OddRCoord:
        """
        https://www.redblobgames.com/grids/hexagons/#conversions-offset
        """
        ...

    def __add__(self, other: Self) -> Self: ...
    def __sub__(self, other: Self) -> Self: ...
    def all_in_range(self, N: int) -> Iterator["_AxialCoord"]:
        """
        https://www.redblobgames.com/grids/hexagons/#range-coordinate
        """
        ...

    @classmethod
    def from_pixel(cls, x: float, y: float, hex_size: float) -> _AxialCoord:
        """
        https://www.redblobgames.com/grids/hexagons/#pixel-to-hex-axial
        https://www.redblobgames.com/grids/hexagons/#pixel-to-hex-mod-origin
        """
        ...

@dataclass(frozen=True)
class _CubeCoord:
    q: int
    r: int
    s: int
    def to_axial(self) -> _AxialCoord:
        """
        https://www.redblobgames.com/grids/hexagons/#conversions-axial
        """
        ...

    def to_odd_r(self) -> OddRCoord: ...
    def get_distance(self, other: Self) -> int:
        """
        https://www.redblobgames.com/grids/hexagons/#distances-cube
        """
        ...

    def line_draw(self, other: Self) -> Iterator["_CubeCoord"]:
        """
        https://www.redblobgames.com/grids/hexagons/#line-drawing
        """
        ...

    def __add__(self, other: Self) -> Self: ...
    def __sub__(self, other: Self) -> Self: ...
    def to_cube_float(
        self, add_epsilon: tuple[float, float, float] | None = None
    ) -> _CubeCoordFloat:
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
        ...

@dataclass(frozen=True)
class _AxialCoordFloat:
    q: float
    r: float
    def to_cube_float(self) -> _CubeCoordFloat:
        """
        https://www.redblobgames.com/grids/hexagons/#conversions-axial
        """
        ...

    def round(self) -> _AxialCoord:
        """
        https://www.redblobgames.com/grids/hexagons/#rounding
        """
        ...

@dataclass(frozen=True)
class _CubeCoordFloat:
    q: float
    r: float
    s: float
    def round(self) -> _CubeCoord: ...
    def lerp(self, other: Self, t: float) -> Self:
        """
        https://www.redblobgames.com/grids/hexagons/#line-drawing
        """
        ...

@dataclass(order=True)
class _AStarCoord:
    priority: float
    coord: OddRCoord = field(compare=False)
