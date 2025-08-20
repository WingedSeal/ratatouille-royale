from .feature import Feature
from .tile import Tile
from .hexagon import OddRCoord
from pathlib import Path

MAP_FILE_EXTENSION = "rrmap"


class Map:
    size_x: int
    size_y: int
    features: list[tuple[Feature, OddRCoord]]
    tiles: list[list[Tile]]

    def __init__(self, size_x: int, size_y: int, tiles: list[list[Tile]]) -> None:
        self.size_x = size_x
        self.size_y = size_y
        self.tiles = tiles

    @classmethod
    def from_file(cls, file: Path) -> "Map":
        pass
        return Map(0, 0, [])
