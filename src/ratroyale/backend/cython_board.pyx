from .hexagon cimport OddRCoord

cpdef list get_attackable_coords(
    object board,
    object rodent,
    object skill
):
    cdef:
        object rodent_tile
        int max_altitude
        int reach
        OddRCoord target_coord
        OddRCoord passed_coord
        object passed_tile
        list attackable_coords = []
    
    rodent_tile = board.get_tile(rodent.pos)
    if rodent_tile is None:
        raise ValueError("Rodent has invalid pos")
    
    max_altitude = rodent_tile.get_total_height(rodent.side) + (skill.altitude or 0)
    reach = skill.reach
    
    if reach is None:
        raise ValueError("'get_attackable_coords is called on skill without reach")
    
    for target_coord in rodent.pos.all_in_range(reach):
        for passed_coord in rodent.pos.line_draw(target_coord):
            passed_tile = board.get_tile(passed_coord)
            if passed_tile is None:
                break
            if passed_tile.get_total_height(rodent.side) > max_altitude:
                break
        else:
            attackable_coords.append(target_coord)
    
    return attackable_coords
