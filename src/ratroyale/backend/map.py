from pprint import pformat
from typing import Any, Final
from .hexagon import OddRCoord
from .side import Side
from .entity import Entity
from .feature import Feature
from .tile import Tile
from pathlib import Path
import inspect


MAP_FILE_EXTENSION = "rrmap"

ENDIAN: Final = "big"


class _DataPointer:
    data: bytes
    pointer: int

    def __init__(self, data: bytes) -> None:
        self.data = data
        self.pointer = 0

    def get_byte(self, size: int = 1) -> int:
        return int.from_bytes(self.get_raw_bytes(size), ENDIAN)

    def get_raw_bytes(self, size: int = 1) -> bytes:
        value = self.data[self.pointer : self.pointer + size]
        self.pointer += size
        return value

    def verify_end(self) -> bool:
        return self.pointer + 1 == len(self.data)


class Map:
    name: str
    size_x: int
    size_y: int
    features: list[Feature]
    tiles: list[list[Tile | None]]
    entities: list[Entity]

    _FORMAT_SPEC = """
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
    """Binary format specification"""

    def __init__(
        self,
        name: str,
        size_x: int,
        size_y: int,
        tiles: list[list[Tile | None]],
        entities: list[Entity] = [],
        features: list[Feature] = [],
    ) -> None:
        self.name = name
        self.size_x = size_x
        self.size_y = size_y
        self.tiles = tiles
        self.entities = entities
        self.features = []
        for feature in features:
            self.add_feature(feature)

    def add_feature(self, feature: Feature) -> None:
        if feature in self.features:
            raise ValueError("This feature already exist in this position")
        self.features.append(feature)
        for pos in feature.shape:
            tile = self.tiles[pos.y][pos.x]
            if tile is None:
                continue
            tile.features.append(feature)

    def remove_feature(self, feature: Feature) -> None:
        self.features.remove(feature)
        for pos in feature.shape:
            tile = self.tiles[pos.y][pos.x]
            if tile is None:
                continue
            tile.features.remove(feature)

    @classmethod
    def from_file(cls, file_path: Path) -> "Map | None":
        with file_path.open("rb") as file:
            data = file.read()
        try:
            return cls.load(data)
        except:
            return None

    def to_file(self, file_path: Path) -> None:
        data = self.save()
        with file_path.open("wb") as file:
            file.write(data)

    def save(self) -> bytes:
        data = bytearray()
        data.append(len(self.name))
        data.extend(self.name.encode())

        large_map_flag = 1 if self.size_x > 255 or self.size_y > 255 else 0
        many_features_flag = 1 if len(self.features) > 255 else 0
        many_entities_flag = 1 if len(self.entities) > 255 else 0

        data.extend(self.size_x.to_bytes(1 + large_map_flag, ENDIAN))
        data.extend(self.size_y.to_bytes(1 + large_map_flag, ENDIAN))

        data.append(
            (large_map_flag << 2) & (many_features_flag << 1) & many_entities_flag
        )

        data.extend(
            (tile.height + 1) if tile is not None else 0
            for row in self.tiles
            for tile in row
        )

        data.extend(len(self.features).to_bytes(1 + many_features_flag, ENDIAN))
        for feature in self.features:
            feature_unique_constructor_flag = (
                1
                if inspect.signature(type(feature).__init__).parameters
                != inspect.signature(Feature.__init__).parameters
                else 0
            )
            feature_id = feature.FEATURE_ID()
            data.extend(
                (feature_id & (feature_unique_constructor_flag << 15)).to_bytes(
                    2, ENDIAN
                )
            )
            data.append(feature.health if feature.health is not None else 0)
            data.append(feature.defense)
            data.append(Side.to_int(feature.side))
            data.append(len(feature.shape))
            for pos in feature.shape:
                data.extend(pos.x.to_bytes(1 + large_map_flag, ENDIAN))
                data.extend(pos.y.to_bytes(1 + large_map_flag, ENDIAN))
            if feature_unique_constructor_flag:
                unique_arguments = _get_unique_init_arguments(feature, Feature)
                data.append(len(unique_arguments))
                data.extend(unique_arguments)

        data.extend(len(self.entities).to_bytes((1 + many_entities_flag), ENDIAN))
        for entity in self.entities:
            entity_unique_constructor_flag = (
                1
                if inspect.signature(type(entity).__init__).parameters
                != inspect.signature(Entity.__init__).parameters
                else 0
            )
            entity_id = entity.PRE_PLACED_ENTITY_ID()
            if entity_id is None:
                raise ValueError(
                    f"Entity of type {type(entity_id)} cannot be pre placed since it has no PRE_PLACED_ENTITY_ID"
                )
            data.extend(
                (entity_id & (entity_unique_constructor_flag << 15)).to_bytes(2, ENDIAN)
            )
            data.extend(entity.pos.x.to_bytes(1 + large_map_flag, ENDIAN))
            data.extend(entity.pos.y.to_bytes(1 + large_map_flag, ENDIAN))
            if entity_unique_constructor_flag:
                unique_arguments = _get_unique_init_arguments(entity, Entity)
                data.append(len(unique_arguments))
                data.extend(unique_arguments)

        return bytes(data)

    @classmethod
    def load(cls, data: bytes) -> "Map":
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
            feature_class_and_unique_constructor_flag = data_pointer.get_byte(2)
            feature_class = Feature.ALL_FEATURES[
                feature_class_and_unique_constructor_flag & ~(1 << 15)
            ]
            unique_constructor_flag = bool(
                feature_class_and_unique_constructor_flag & (1 << 15)
            )
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

            features.append(
                feature_class(shape, health, defense, side, *feature_unique_parameters)
            )

        entity_count = data_pointer.get_byte(1 + many_entities_flag)
        entities: list[Entity] = []

        for _ in range(entity_count):
            entity_class_and_unique_constructor_flag = data_pointer.get_byte(2)
            entity_class = Entity.PRE_PLACED_ENTITIES[
                entity_class_and_unique_constructor_flag & ~(1 << 15)
            ]
            unique_constructor_flag = bool(
                entity_class_and_unique_constructor_flag & (1 << 15)
            )
            side = Side.from_int(data_pointer.get_byte())
            x = data_pointer.get_byte(coord_size)
            y = data_pointer.get_byte(coord_size)
            entity_unique_parameters: list[int] = []
            if unique_constructor_flag:
                unique_parameter_count = data_pointer.get_byte()
                for _ in range(unique_parameter_count):
                    entity_unique_parameters.append(data_pointer.get_byte())
            entities.append(
                entity_class(OddRCoord(x, y), side, *entity_unique_parameters)
            )

        assert data_pointer.verify_end()

        return cls(name, size_x, size_y, tiles, entities, features)

    def __repr__(self) -> str:
        return f"""Map(
    name={self.name!r},
    size_x={self.size_x},
    size_y={self.size_y},
    features={pformat(self.features)},
    tiles={pformat(self.tiles)},
    entities={pformat(self.entities)},
)"""

    def __str__(self) -> str:
        simple_tiles = [
            [str(tile) if tile else None for tile in row] for row in self.tiles
        ]
        simple_features = [str(f) for f in self.features]
        simple_entities = [str(e) for e in self.entities]
        return f"""Map(
    name={self.name!r},
    size_x={self.size_x},
    size_y={self.size_y},
    features={pformat(simple_features)},
    tiles={pformat(simple_tiles)},
    entities={pformat(simple_entities)},
)"""


# def _get_unique_feature_arguments(feature: Feature) -> tuple[int]:
#     base_fields = {field.name for field in fields(Feature)}
#     unique_arguments = tuple(getattr(feature, field.name) for field in fields(
#         type(feature)) if field.name not in base_fields)
#     for arg in unique_arguments:
#         if not type(arg) != int:
#             raise ValueError(
#                 f"A Feature contains a field that is not integer")
#         if int(arg) > 255:
#             raise ValueError(
#                 f"A Feature contains a field that is too large")
#     return unique_arguments


def _get_unique_init_arguments(obj: Any, basecls: type) -> tuple[int]:
    obj_class = type(obj)
    if not issubclass(obj_class, basecls):
        raise TypeError(f"{basecls} is not a base class of {obj_class}")
    derived_signatures = inspect.signature(obj_class.__init__)
    base_signatures = inspect.signature(basecls.__init__)  # type: ignore[misc]

    derived_params = set(derived_signatures.parameters.keys()) - {"self"}
    base_params = set(base_signatures.parameters.keys()) - {"self"}

    unique_params = derived_params - base_params
    return tuple(getattr(obj, name) for name in unique_params)
