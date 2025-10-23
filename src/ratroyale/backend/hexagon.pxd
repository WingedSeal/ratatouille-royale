cdef class _AxialCoord
cdef class OddRCoord
cdef class _CubeCoord
cdef class _CubeCoordFloat

cdef class _CubeCoordFloat:
    cdef public double q, r, s
    cpdef _CubeCoord round(self)
    cpdef _CubeCoordFloat lerp(self, _CubeCoordFloat other, double t)

cdef class _CubeCoord:
    cdef public double q, r, s
    cpdef _AxialCoord to_axial(self)
    cpdef OddRCoord to_odd_r(self)
    cpdef int get_distance(self, _CubeCoord other)
    cpdef _CubeCoordFloat to_cube_float(
        self, tuple add_epsilon = *
    )

cdef class _AxialCoord:
    cdef public int q, r
    cpdef _CubeCoord to_cube(self)
    cpdef OddRCoord to_odd_r(self)

cdef class OddRCoord:
    cdef public int x, y
    cpdef list[OddRCoord] path_find(
        self,
        OddRCoord goal,
        object is_coord_blocked,
        get_cost: Callable[[OddRCoord, OddRCoord], float] = *,
    )
    cpdef set[OddRCoord] get_reachable_coords(
        self,
        int reach,
        object is_coord_blocked = *,
        bint is_include_self = *,
    )
    cpdef OddRCoord get_neighbor(self, int direction)
    cpdef tuple[double, double] to_pixel(
        self,
        double hex_width,
        double hex_height = *,
        bint is_bounding_box = *,
    )
    cpdef int get_distance(self, OddRCoord other)
    cpdef _CubeCoord to_cube(self)
    cpdef _AxialCoord to_axial(self)
