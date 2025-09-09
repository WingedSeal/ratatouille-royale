from .hexagon import OddRCoord
from .side import Side
from .entity import Entity
from .feature import Feature
from .tile import Tile
from pathlib import Path

MAP_FILE_EXTENSION = "rrmap"


class _DataPointer:
    data: bytes
    pointer: int

    def __init__(self, data: bytes) -> None:
        self.data = data
        self.pointer = 0

    def get_byte(self, size: int = 1) -> int:
        return int.from_bytes(self.get_raw_bytes(size), 'big')

    def get_raw_bytes(self, size: int = 1) -> bytes:
        value = self.data[self.pointer:self.pointer + size]
        self.pointer += size
        return value


class Map:
    name: str
    size_x: int
    size_y: int
    features: list[Feature]
    tiles: list[list[Tile]]
    entities: list[Entity]

    def __init__(self, size_x: int, size_y: int, tiles: list[list[Tile]], entities: list[Entity] = [], features: list[Feature] = []) -> None:
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
            self.tiles[pos.y][pos.x].features.append(feature)

    def remove_feature(self, feature: Feature):
        self.features.remove(feature)
        for pos in feature.shape:
            self.tiles[pos.y][pos.x].features.remove(feature)

    @classmethod
    def from_file(cls, file: Path) -> "Map":
        return cls(0, 0, [])

    @classmethod
    def load(cls, data: bytes) -> "Map":
        """
        1 byte for map_name_length
        map_name_length byte for `name`
        5 bits 
        1 bit for large_map_flag
        1 bit for many_features_flag
        1 bit for many_entities_flag
        (1 + large_map_flag) bytes for `size_x`
        (1 + large_map_flag) bytes for `size_y`

        loop (`size_x`*`size_y`) times {
            1 byte for tile's `height` (`None if byte == 0 else byte - 1`)
        }

        (1 + many_features_flag) byte for feature_count
        loop feature_count times {
            1 bit for feature_unique_constructor_flag
            15 bits for feature's class
            1 byte for feature's `health` (`None if byte == 0 else byte`)
            1 byte for feature's `defense`
            1 byte for feature's `side`
            1 byte for shape_size
            loop shape_size times {
                (1 + large_map_flag) bytes for shape's `OddRCoord.x`
                (1 + large_map_flag) bytes for shape's `OddRCoord.y`
            }
            if feature_unique_constructor_flag {
                1 byte for unique_parameter_count 
                loop unique_parameter_count {
                    1 byte for feature's unique parameter
                }
            }
        }

        (1 + many_entities_flag) byte for entity_count
        loop entity_count times {
            1 bit for entity_unique_constructor_flag
            15 bits for entity's class
            1 byte for entity's `side`
            (1 + large_map_flag) bytes for entity's `OddRCoord.x`
            (1 + large_map_flag) bytes for entity's `OddRCoord.y`
            if entity_unique_constructor_flag {
                1 byte for unique_parameter_count 
                loop unique_parameter_count {
                    1 byte for entity's unique parameter
                }
            }
        }
        """
        data_pointer = _DataPointer(data)
        map_name_length = data_pointer.get_byte()
        name = data_pointer.get_raw_bytes(map_name_length).decode()
        flags = data_pointer.get_byte()
        large_map_flag = bool(flags & 1 << 2)
        many_features_flag = bool(flags & 1 << 1)
        many_entities_flag = bool(flags & 1 << 0)

        coord_size = 1 + large_map_flag
        size_x = data_pointer.get_byte(coord_size)
        size_y = data_pointer.get_byte(coord_size)

        tiles: list[list[Tile | None]] = []
        for y in range(size_y):
            tiles.append([])
            for x in range(size_x):
                height_byte = data_pointer.get_byte()
                height = None if height_byte == 0 else height_byte - 1
                if height is None:
                    tiles[y].append(None)
                else:
                    tiles[y].append(Tile(OddRCoord(x, y), height))

        feature_count = data_pointer.get_byte(1 + many_features_flag)
        features: list[Feature] = []

        for _ in range(feature_count):
            feature_class_and_unique_constructor_flag = data_pointer.get_byte(
                2)
            feature_class = Feature.ALL_FEATURES[feature_class_and_unique_constructor_flag & ~(
                1 << 15)]
            unique_constructor_flag = bool(feature_class_and_unique_constructor_flag & (
                1 << 15))
            health_byte = data_pointer.get_byte()
            health = None if health_byte == 0 else health_byte
            defense = data_pointer.get_byte()
            side = Side.from_int(data_pointer.get_byte())
            shape_size = data_pointer.get_byte()

            shape: list[OddRCoord] = []
            for _ in range(shape_size):
                x = data_pointer.get_byte(coord_size)
                y = data_pointer.get_byte(coord_size)
                shape.append(OddRCoord(x, y))

            feature_unique_parameters: list[int] = []
            if unique_constructor_flag:
                unique_parameter_count = data_pointer.get_byte()
                for _ in range(unique_parameter_count):
                    feature_unique_parameters.append(data_pointer.get_byte())

            features.append(feature_class(
                shape, health, defense, side, *feature_unique_parameters))

        entity_count = data_pointer.get_byte(1 + many_entities_flag)
        entities: list[Entity] = []

        for _ in range(entity_count):
            entity_class_and_unique_constructor_flag = data_pointer.get_byte(
                2)
            entity_class = Entity.PRE_PLACED_ENTITIES[entity_class_and_unique_constructor_flag & ~(
                1 << 15)]
            unique_constructor_flag = bool(entity_class_and_unique_constructor_flag & (
                1 << 15))
            side = Side.from_int(data_pointer.get_byte())
            x = data_pointer.get_byte(coord_size)
            y = data_pointer.get_byte(coord_size)
            entity_unique_parameters: list[int] = []
            if unique_constructor_flag:
                unique_parameter_count = data_pointer.get_byte()
                for _ in range(unique_parameter_count):
                    entity_unique_parameters.append(data_pointer.get_byte())
            entities.append(entity_class(
                OddRCoord(x, y), side, *entity_unique_parameters))

        return cls(size_x, size_y, tiles, entities, features)
