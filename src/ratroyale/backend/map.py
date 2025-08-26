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
        self.features = []
        for feature, feature_pos in features:
            self.add_feature(feature, feature_pos)

    def add_feature(self, feature: Feature, pos: OddRCoord):
        if (feature, pos) in self.features:
            raise ValueError("This feature already exist in this position")
        self.features.append((feature, pos))
        for coord in feature.shape:
            self.tiles[pos.y + coord.y][pos.x +
                                        coord.x].features.append(feature)

    def remove_feature_index(self, index: int):
        feature, pos = self.features[index]
        for coord in feature.shape:
            self.tiles[pos.y + coord.y][pos.x +
                                        coord.x].features.remove(feature)
        del self.features[index]

    def remove_feature(self, feature: Feature, pos: OddRCoord):
        self.features.remove((feature, pos))
        for coord in feature.shape:
            self.tiles[pos.y + coord.y][pos.x +
                                        coord.x].features.remove(feature)

    @classmethod
    def from_file(cls, file: Path) -> "Map":
        # TODO
        return cls(0, 0, [])
