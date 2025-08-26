from .entity import Entity
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
    entities: list[Entity]

    def __init__(self, size_x: int, size_y: int, tiles: list[list[Tile]], entities: list[Entity] = [], features: list[tuple[Feature, OddRCoord]] = []) -> None:
        self.size_x = size_x
        self.size_y = size_y
        self.tiles = tiles
        self.entities = entities
        for feature, feature_pos in features:
            for coord in feature.shape:
                self.tiles[feature_pos.y + coord.y][feature_pos.x +
                                                    coord.x].features.add(feature)

    @classmethod
    def from_file(cls, file: Path) -> "Map":
        # TODO
        return cls(0, 0, [])
