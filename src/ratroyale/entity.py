from .hexagon import OddRCoord


class Entity:
    """
    Any entity on the tile system.
    """
    pos: OddRCoord

    def __init__(self, pos: OddRCoord) -> None:
        self.pos = pos
