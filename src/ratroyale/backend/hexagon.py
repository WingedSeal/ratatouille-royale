from queue import PriorityQueue
from dataclasses import dataclass, field
from typing import Callable, Iterator, Protocol, Self, overload
from ..utils import lerp
from math import sqrt


class IsCoordBlocked(Protocol):
    """
    A callback function that evaluate whether target coord is accessible from source coord 
    """

    def __call__(self, target_coord: "OddRCoord", source_coord: "OddRCoord") -> bool:
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

    DIRECTION_DIFFERENCES = (
        # Even Rows
        ((+1,  0), (0, -1), (-1, -1),
         (-1,  0), (-1, +1), (0, +1)),
        # Odd Rows
        ((+1,  0), (+1, -1), (0, -1),
         (-1,  0), (0, +1), (+1, +1)),
    )

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

    def line_draw(self, other: Self) -> Iterator["OddRCoord"]:
        return (cube.to_odd_r() for cube in self.to_cube().line_draw(other.to_cube()))

    def all_in_range(self, N: int) -> Iterator["OddRCoord"]:
        return (axial.to_odd_r() for axial in self.to_axial().all_in_range(N))

    @overload
    def to_pixel(self, hex_size: float,
                 is_bounding_box: bool = False) -> tuple[float, float]: ...

    @overload
    def to_pixel(self, hex_width: float,
                 hex_height: float, is_bounding_box: bool = False) -> tuple[float, float]: ...

    def to_pixel(  # type: ignore
            self, hex_width: float, hex_height: float | None = None, is_bounding_box: bool = False
    ) -> tuple[float, float]:
        """
        https://www.redblobgames.com/grids/hexagons/#hex-to-pixel-offset
        https://www.redblobgames.com/grids/hexagons/#hex-to-pixel-mod-origin
        is_bounding_box: Whether hex_width and hex_height specify the hexagon's bounding box instead of its radius.
        """
        if hex_height is None:
            hex_height = hex_width
        if is_bounding_box:
            hex_width /= sqrt(3)
            hex_height *= 0.5
        x = sqrt(3) * (self.col + 0.5 * (self.row & 1))
        y = 1.5 * self.row
        # Origin is not on the center of odd-r (0,0)
        x += 1
        y += sqrt(3) / 2  # https://www.redblobgames.com/grids/hexagons/#basics

        return x * hex_width, y * hex_height

    def get_neighbor(self, direction: int) -> "OddRCoord":
        """
        Get neighbor on a specific direction
        :param direction: The direction to get the neighbor, ranges between 0 (top left) to 5 (left)
        :returns: Neighbor coord
        """
        if direction not in range(0, 6):
            raise ValueError("direction must be between 0 and 5")
        parity = self.row & 1
        diff = self.DIRECTION_DIFFERENCES[parity][direction]
        return OddRCoord(self.col + diff[0], self.row + diff[1])

    def get_neighbors(self) -> Iterator["OddRCoord"]:
        """
        Get all 6 neighbors
        """
        for i in range(6):
            yield self.get_neighbor(i)

    def get_reachable_coords(self, reach: int, is_coord_blocked: IsCoordBlocked, *, is_include_self: bool = False) -> set["OddRCoord"]:
        """
        Get every reachable coords within reach
        https://www.redblobgames.com/grids/hexagons/#range-obstacles

        :param reach: Movement from original coord
        :param is_coord_blocked: A callback function that evaluate whether target coord is accessible from source coord 
        :returns: Reachable coords
        """
        visited: set[OddRCoord] = set()
        visited.add(self)
        fringes: list[list[OddRCoord]] = []
        fringes.append([self])

        for k in range(reach):
            fringes.append([])
            for coord in fringes[k]:
                for neighbor in coord.get_neighbors():
                    if neighbor not in visited and not is_coord_blocked(neighbor, coord):
                        visited.add(neighbor)
                        fringes[k + 1].append(neighbor)

        if not is_include_self:
            visited.remove(self)

        return visited

    @classmethod
    def from_pixel(cls, x: float, y: float, hex_size: float) -> "OddRCoord":
        return _AxialCoord.from_pixel(x, y, hex_size).to_odd_r()

    def __add__(self, other: Self) -> Self:
        return self.__class__(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Self) -> Self:
        return self.__class__(self.x - other.x, self.y - other.y)

    def path_find(self,
                  goal: "OddRCoord",
                  is_coord_blocked: IsCoordBlocked,
                  get_cost: Callable[["OddRCoord", "OddRCoord"], float] = lambda a, b: 1.0) -> list["OddRCoord"] | None:
        """
        https://www.redblobgames.com/pathfinding/a-star/introduction.html#astar

        Using A-star method to path find to a goal

        :param goal: Goal coord
        :param is_coord_blocked: A callback function that evaluate whether target coord is accessible from source coord 
        :param get_cost: A callback function to evaluate cost to travel from first coord to second coord, defaults to `lambda: a, b: 1.0`
        :returns: Path calculated or None if goal is not reachable
        """
        frontier: PriorityQueue[_AStarCoord] = PriorityQueue()
        frontier.put(_AStarCoord(0, self))
        came_from: dict[OddRCoord, OddRCoord | None] = {
            self: None
        }
        cost_so_far: dict[OddRCoord, float] = {
            self: 0
        }

        while not frontier.empty():
            current = frontier.get().coord
            if current == goal:
                break
            for next_coord in current.get_neighbors():
                if is_coord_blocked(next_coord, current):
                    continue

                new_cost = cost_so_far[current] + get_cost(current, next_coord)

                if next_coord not in cost_so_far or new_cost < cost_so_far[next_coord]:
                    cost_so_far[next_coord] = new_cost
                    priority = new_cost + goal.get_distance(next_coord)
                    frontier.put(_AStarCoord(priority, next_coord))
                    came_from[next_coord] = current

        if goal not in came_from:
            return None

        path = []
        current_: OddRCoord | None = goal
        while current_ is not None:
            path.append(current_)
            current_ = came_from[current_]
        path.reverse()
        return path

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"


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

    def __add__(self, other: Self) -> Self:
        return self.__class__(self.q + other.q, self.r + other.r)

    def __sub__(self, other: Self) -> Self:
        return self.__class__(self.q - other.q, self.r - other.r)

    def all_in_range(self, N: int) -> Iterator["_AxialCoord"]:
        """
        https://www.redblobgames.com/grids/hexagons/#range-coordinate
        """
        for q in range(-N, N+1):
            for r in range(max(-N, -q-N), min(N, -q+N) + 1):
                yield self + _AxialCoord(q, r)

    @classmethod
    def from_pixel(cls, x: float, y: float, hex_size: float) -> "_AxialCoord":
        """
        https://www.redblobgames.com/grids/hexagons/#pixel-to-hex-axial
        https://www.redblobgames.com/grids/hexagons/#pixel-to-hex-mod-origin
        """
        x /= hex_size
        y /= hex_size
        # Origin is not on the center of odd-r (0,0)
        x -= 1
        y -= sqrt(3) / 2  # https://www.redblobgames.com/grids/hexagons/#basics

        q = sqrt(3)/3 * x - 1/3 * y
        r = 2/3 * y
        return _AxialCoordFloat(q, r).round()


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

    def __add__(self, other: Self) -> Self:
        return self.__class__(self.q + other.q, self.r + other.r, self.s + other.s)

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
class _AxialCoordFloat:
    q: float
    r: float

    def to_cube_float(self) -> "_CubeCoordFloat":
        """
        https://www.redblobgames.com/grids/hexagons/#conversions-axial
        """
        return _CubeCoordFloat(self.q, self.r, -self.q-self.r)

    def round(self) -> "_AxialCoord":
        return self.to_cube_float().round().to_axial()


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


@dataclass(order=True)
class _AStarCoord:
    priority: float
    coord: OddRCoord = field(compare=False)
