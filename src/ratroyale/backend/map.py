from .entity import Entity
from .feature import Feature
from .tile import Tile
from pathlib import Path

MAP_FILE_EXTENSION = "rrmap"


class Map:
    size_x: int
    size_y: int
    features: list[Feature]
    tiles: list[list[Tile | None]]
    entities: list[Entity]

    def __init__(self, size_x: int, size_y: int, tiles: list[list[Tile | None]], entities: list[Entity] = [], features: list[Feature] = []) -> None:
        self.size_x = size_x
        self.size_y = size_y
        self.tiles = tiles
        self.entities = entities
        self.features = []
        for feature in features:
            self.add_feature(feature)

    def add_feature(self, feature: Feature):
        if feature in self.features:
            raise ValueError("This feature already exist in this position")
        self.features.append(feature)
        for pos in feature.shape:
            tile = self.tiles[pos.y][pos.x]
            if tile is None:
                continue
            tile.features.append(feature)
            
    def remove_feature(self, feature: Feature):
        self.features.remove(feature)
        for pos in feature.shape:
            tile = self.tiles[pos.y][pos.x]
            if tile is None:
                continue
            tile.features.remove(feature)
            

    @classmethod
    def from_file(cls, file: Path) -> "Map":
        # TODO
        return cls(0, 0, [])
