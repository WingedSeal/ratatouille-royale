# distutils: language = c

from libc.math cimport sqrt, fabs as c_abs
from queue import PriorityQueue
from typing import Callable, Iterator, Self

# Re-import Python's round (or just use it directly, as it's a built-in)
# The Cython compiler handles the built-in round function.

cdef double lerp(double a, double b, double t) except *

cdef class _AxialCoord
cdef class _CubeCoord
cdef class OddRCoord

cdef class IsCoordBlocked:
    cpdef bint __call__(self, OddRCoord target_coord, OddRCoord source_coord):
        pass

cdef bint _coord_never_blocked(OddRCoord target_coord, OddRCoord source_coord):
    return 0


cdef class _AStarCoord:
    cdef double priority
    cdef OddRCoord coord

    def __init__(self, priority: float, coord: OddRCoord):
        self.priority = priority
        self.coord = coord

    def __lt__(self, other):
        return self.priority < other.priority
    
    def __eq__(self, other):
        return self.priority == other.priority


cdef class _CubeCoord:
    cdef int q, r, s

    def __init__(self, int q, int r, int s):
        self.q = q
        self.r = r
        self.s = s

    def __hash__(self):
        return hash((self.q, self.r, self.s))

    def __eq__(self, other):
        if not isinstance(other, _CubeCoord): return False
        return self.q == other.q and self.r == other.r and self.s == other.s

    cpdef _AxialCoord to_axial(self) except *:
        return _AxialCoord(self.q, self.r)

    cpdef OddRCoord to_odd_r(self) except *:
        return self.to_axial().to_odd_r()

    cpdef int get_distance(self, _CubeCoord other) except *:
        cdef _CubeCoord vec = self - other
        return (c_abs(vec.q) + c_abs(vec.r) + c_abs(vec.s)) // 2

    def line_draw(self, other: Self) -> Iterator[OddRCoord]:
        cdef int N = self.get_distance(other)
        cdef int i
        cdef _CubeCoordFloat self_float = self.to_cube_float(add_epsilon=(1e-6, 2e-6, -3e-6))
        cdef _CubeCoordFloat other_float = other.to_cube_float()

        for i in range(N + 1):
            yield self_float.lerp(
                other_float, <double>i / <double>N
            ).round()

    cpdef _CubeCoord __add__(self, _CubeCoord other) except *:
        return _CubeCoord(self.q + other.q, self.r + other.r, self.s + other.s)

    cpdef _CubeCoord __sub__(self, _CubeCoord other) except *:
        return _CubeCoord(self.q - other.q, self.r - other.r, self.s - other.s)

    cpdef _CubeCoordFloat to_cube_float(
        self, tuple[float, float, float] add_epsilon = None
    ) except *:
        if add_epsilon is None:
            return _CubeCoordFloat(self.q, self.r, self.s)
        else:
            return _CubeCoordFloat(
                self.q + add_epsilon[0],
                self.r + add_epsilon[1],
                self.s + add_epsilon[2],
            )


cdef class _AxialCoord:
    cdef int q, r

    def __init__(self, int q, int r):
        self.q = q
        self.r = r

    def __hash__(self):
        return hash((self.q, self.r))

    def __eq__(self, other):
        if not isinstance(other, _AxialCoord): return False
        return self.q == other.q and self.r == other.r

    cpdef _CubeCoord to_cube(self) except *:
        return _CubeCoord(self.q, self.r, -self.q - self.r)

    cpdef OddRCoord to_odd_r(self) except *:
        cdef int parity = self.r & 1
        cdef int col = self.q + (self.r - parity) // 2
        cdef int row = self.r
        return OddRCoord(col, row)

    cpdef _AxialCoord __add__(self, _AxialCoord other) except *:
        return _AxialCoord(self.q + other.q, self.r + other.r)

    cpdef _AxialCoord __sub__(self, _AxialCoord other) except *:
        return _AxialCoord(self.q - other.q, self.r - other.r)

    def all_in_range(self, N: int) -> Iterator[OddRCoord]:
        cdef int q, r
        cdef _AxialCoord offset_coord
        
        for q in range(-N, N + 1):
            for r in range(max(-N, -q - N), min(N, -q + N) + 1):
                offset_coord = self + _AxialCoord(q, r)
                yield offset_coord.to_odd_r()

    @classmethod
    cpdef _AxialCoord from_pixel(cls, double x, double y, double hex_size) except *:
        cdef double _x = x / hex_size
        cdef double _y = y / hex_size
        cdef double q, r
        
        _x -= 1.0
        _y -= sqrt(3.0) / 2.0

        q = sqrt(3.0) / 3.0 * _x - 1.0 / 3.0 * _y
        r = 2.0 / 3.0 * _y
        return _AxialCoordFloat(q, r).round()


cdef class _CubeCoordFloat:
    cdef double q, r, s

    def __init__(self, double q, double r, double s):
        self.q = q
        self.r = r
        self.s = s

    cpdef _CubeCoord round(self) except *:
        # Using Python's built-in round()
        cdef int round_q = <int>round(self.q)
        cdef int round_r = <int>round(self.r)
        cdef int round_s = <int>round(self.s)
        cdef double q_diff, r_diff, s_diff

        q_diff = c_abs(round_q - self.q)
        r_diff = c_abs(round_r - self.r)
        s_diff = c_abs(round_s - self.s)

        if q_diff > r_diff and q_diff > s_diff:
            round_q = -round_r - round_s
        elif r_diff > s_diff:
            round_r = -round_q - round_s
        else:
            round_s = -round_q - round_r

        return _CubeCoord(round_q, round_r, round_s)

    cpdef _CubeCoordFloat lerp(self, _CubeCoordFloat other, double t) except *:
        return _CubeCoordFloat(
            lerp(self.q, other.q, t),
            lerp(self.r, other.r, t),
            lerp(self.s, other.s, t),
        )

cdef class _AxialCoordFloat:
    cdef double q, r

    def __init__(self, double q, double r):
        self.q = q
        self.r = r

    cpdef _CubeCoordFloat to_cube_float(self) except *:
        return _CubeCoordFloat(self.q, self.r, -self.q - self.r)

    cpdef _AxialCoord round(self) except *:
        return self.to_cube_float().round().to_axial()


cdef class OddRCoord:
    cdef public int x, y

    DIRECTION_DIFFERENCES = (
        ((+1, 0), (0, -1), (-1, -1), (-1, 0), (-1, +1), (0, +1)),
        ((+1, 0), (+1, -1), (0, -1), (-1, 0), (0, +1), (+1, +1)),
    )

    def __init__(self, int x, int y):
        self.x = x
        self.y = y

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        if not isinstance(other, OddRCoord): return False
        return self.x == other.x and self.y == other.y

    @property
    def row(self) -> int:
        return self.y

    @property
    def col(self) -> int:
        return self.x

    cpdef _AxialCoord to_axial(self) except *:
        cdef int parity = self.y & 1
        cdef int q = self.x - (self.y - parity) // 2
        cdef int r = self.y
        return _AxialCoord(q, r)

    cpdef _CubeCoord to_cube(self) except *:
        return self.to_axial().to_cube()

    cpdef int get_distance(self, OddRCoord other) except *:
        return self.to_cube().get_distance(other.to_cube())

    def line_draw(self, other: Self) -> Iterator[OddRCoord]:
        return (cube.to_odd_r() for cube in self.to_cube().line_draw(other.to_cube()))

    def all_in_range(self, N: int) -> Iterator[OddRCoord]:
        return self.to_axial().all_in_range(N)

    cpdef tuple[double, double] to_pixel(
        self,
        double hex_width,
        double hex_height = -1.0,
        bint is_bounding_box = 0,
    ) except *:
        cdef double _hex_width = hex_width
        cdef double _hex_height
        cdef double x, y
        
        if hex_height == -1.0:
            _hex_height = hex_width
        else:
            _hex_height = hex_height
            
        if is_bounding_box:
            _hex_width /= sqrt(3.0)
            _hex_height *= 0.5
            
        x = sqrt(3.0) * (self.x + 0.5 * (self.y & 1))
        y = 1.5 * self.y
        x += 1.0
        y += sqrt(3.0) / 2.0
        
        return x * _hex_width, y * _hex_height

    cpdef OddRCoord get_neighbor(self, int direction) except *:
        cdef int parity
        cdef tuple diff
        cdef int dx, dy
        
        if direction < 0 or direction > 5:
            raise ValueError("direction must be between 0 and 5")
            
        parity = self.y & 1
        diff = self.DIRECTION_DIFFERENCES[parity][direction]
        dx, dy = diff
        return OddRCoord(self.x + dx, self.y + dy)

    def get_neighbors(self) -> Iterator[OddRCoord]:
        cdef int i
        for i in range(6):
            yield self.get_neighbor(i)

    def get_reachable_coords(
        self,
        int reach,
        IsCoordBlocked is_coord_blocked = _coord_never_blocked,
        *,
        bint is_include_self = 0,
    ) -> set[OddRCoord]:
        cdef set visited = set()
        cdef list fringes = []
        cdef int k
        cdef OddRCoord coord, neighbor
        
        visited.add(self)
        fringes.append([self])

        for k in range(reach):
            fringes.append([])
            for coord in fringes[k]:
                for neighbor in coord.get_neighbors():
                    if neighbor not in visited and not is_coord_blocked(neighbor, coord):
                        visited.add(neighbor)
                        fringes[k + 1].append(neighbor)

        if not is_include_self:
            visited.discard(self)

        return visited

    @classmethod
    cpdef OddRCoord from_pixel(cls, double x, double y, double hex_size) except *:
        return _AxialCoord.from_pixel(x, y, hex_size).to_odd_r()

    cpdef OddRCoord __add__(self, OddRCoord other) except *:
        return OddRCoord(self.x + other.x, self.y + other.y)

    cpdef OddRCoord __sub__(self, OddRCoord other) except *:
        return OddRCoord(self.x - other.x, self.y - other.y)

    def path_find(
        self,
        OddRCoord goal,
        IsCoordBlocked is_coord_blocked,
        get_cost: Callable[[OddRCoord, OddRCoord], float] = lambda a, b: 1.0,
    ) -> list[OddRCoord] | None:
        cdef PriorityQueue frontier = PriorityQueue()
        cdef dict came_from = {self: None}
        cdef dict cost_so_far = {self: 0.0}
        cdef OddRCoord current
        cdef OddRCoord next_coord
        cdef double new_cost, priority
        cdef list path
        cdef OddRCoord current_
        cdef _AStarCoord frontier_item

        frontier.put(_AStarCoord(0.0, self))

        while not frontier.empty():
            frontier_item = frontier.get()
            current = frontier_item.coord
            
            if current == goal:
                break
            
            for next_coord in current.get_neighbors():
                if is_coord_blocked(next_coord, current):
                    continue

                new_cost = cost_so_far[current] + get_cost(current, next_coord)

                if next_coord not in cost_so_far or new_cost < cost_so_far[next_coord]:
                    cost_so_far[next_coord] = new_cost
                    priority = new_cost + <double>goal.get_distance(next_coord)
                    frontier.put(_AStarCoord(priority, next_coord))
                    came_from[next_coord] = current

        if goal not in came_from:
            return None

        path = []
        current_ = goal
        while current_ is not None:
            path.append(current_)
            current_ = came_from[current_]
        
        path.pop()
        path.reverse()
        return path

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"
