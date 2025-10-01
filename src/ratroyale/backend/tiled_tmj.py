from typing import TYPE_CHECKING, Any, Literal, cast, get_args
from itertools import count
from pathlib import Path
from .entity import Entity
from .feature import Feature
from .hexagon import OddRCoord
from .side import Side
from .tile import Tile
from .map import Map

try:
    import numpy as np
    from PIL import Image, ImageDraw, ImageChops
except ImportError:
    if TYPE_CHECKING:
        import numpy as np
        from PIL import Image, ImageDraw, ImageChops

TILED_TILE_PIXEL = 50


LayerName = Literal[
    "tile_id",
    "height",
    "feature_group",
    "feature_class",
    "feature_health",
    "feature_defense",
    "feature_side",
    "feature_extra_count",
    "entity_class",
    "entity_side",
    "entity_extra_count",
]

LAYER_NAMES: dict[LayerName, int] = {
    value: index for index, value in enumerate(get_args(LayerName))
}


def _get_tile_data_value(
    tile_data: "np.typing.NDArray[np.uint32]", layer_name: LayerName
) -> np.int32:
    return tile_data[LAYER_NAMES[layer_name]]


def _reconstruct_layer_data(
    layers_data: "dict[str, np.typing.NDArray[np.uint8]]",
    layer_name: LayerName,
    fallback_length: int,
) -> "np.typing.NDArray[np.uint32]":
    """Supports _e2, _e4, ... suffix"""
    if layer_name not in layers_data:
        return np.zeros(fallback_length, dtype=np.uint32)
    data = layers_data[layer_name]
    base_data: np.typing.NDArray[np.uint32] = data.astype("uint32")
    for i in count(start=2, step=2):
        if f"{layer_name}_e{i}" not in layers_data:
            break
        base_data += layers_data[f"{layer_name}_e{i}"].astype("uint32") * (10**i)
    return base_data


def _process_tile(
    tile_data: np.typing.NDArray[np.uint32],
    tiles: list[list[Tile | None]],
    coord: OddRCoord,
) -> None:
    tile_id = _get_tile_data_value(tile_data, "tile_id")
    if tile_id == 0:
        tiles[-1].append(None)
        return
    tile = Tile(
        tile_id.item(),
        coord,
        _get_tile_data_value(tile_data, "height").item(),
    )

    tiles[-1].append(tile)


def _process_feature(
    tile_data: "np.typing.NDArray[np.uint32]",
    features_from_group: dict[int, Feature | list[OddRCoord]],
    layers_data: "dict[str, np.typing.NDArray[np.uint8]]",
    coord: OddRCoord,
) -> None:
    feature_group = _get_tile_data_value(tile_data, "feature_group")
    if feature_group == 0:
        return
    feature_class = _get_tile_data_value(tile_data, "feature_class")
    if feature_group not in features_from_group:
        features_from_group[feature_group.item()] = []
    feature_or_shape = features_from_group[feature_group.item()]
    if isinstance(feature_or_shape, list):
        feature_or_shape.append(coord)
        if feature_class == 0:
            return
        extra_params = (
            layers_data[f"feature_extra{i}"].item()
            for i in range(_get_tile_data_value(tile_data, "feature_extra_count"))
        )
        new_feature = Feature.ALL_FEATURES[feature_class.item()](
            feature_or_shape,
            _get_tile_data_value(tile_data, "feature_health").item(),
            _get_tile_data_value(tile_data, "feature_defense").item(),
            Side.from_int(_get_tile_data_value(tile_data, "feature_side").item()),
            *extra_params,
        )
        features_from_group[feature_group.item()] = new_feature
    elif isinstance(feature_or_shape, Feature):
        feature_or_shape.shape.append(coord)


def _process_entity(
    tile_data: "np.typing.NDArray[np.uint32]",
    entities: list[Entity],
    layers_data: "dict[str, np.typing.NDArray[np.uint8]]",
    coord: OddRCoord,
) -> None:
    entity_class = _get_tile_data_value(tile_data, "entity_class")
    if entity_class == 0:
        return
    extra_params = (
        layers_data[f"entity_extra{i}"].item()
        for i in range(_get_tile_data_value(tile_data, "entity_extra_count"))
    )
    entity = Entity.PRE_PLACED_ENTITIES[entity_class.item()](
        coord,
        Side.from_int(_get_tile_data_value(tile_data, "entity_side").item()),
        *extra_params,
    )
    entities.append(entity)


def tmj_to_map(tmj_data: dict[str, Any], map_name: str) -> Map:
    layers: list[dict[str, Any]] = tmj_data["layers"]
    size_y: int = tmj_data["height"]
    size_x: int = tmj_data["width"]
    layers_data: dict[str, np.typing.NDArray[np.uint8]] = {}
    for layer in layers:
        with np.errstate(over="raise"):
            layers_data[layer["name"]] = np.array(layer["data"], dtype="uint8")
    tiles_data = np.hstack(
        [
            _reconstruct_layer_data(layers_data, layer_name, size_x * size_y)
            for layer_name in LAYER_NAMES
        ]
    )
    tiles: list[list[Tile | None]] = [[] for _ in range(size_y)]
    features_from_group: dict[int, Feature | list[OddRCoord]] = {}
    entities: list[Entity] = []
    for i, tile_data in enumerate(tiles_data):
        tile_data = cast(np.typing.NDArray[np.uint32], tile_data)
        row, col = divmod(i, size_x)
        coord = OddRCoord(col, row)

        _process_tile(tile_data, tiles, coord)
        _process_feature(tile_data, features_from_group, layers_data, coord)
        _process_entity(tile_data, entities, layers_data, coord)

    features = [
        feature
        for feature in features_from_group.values()
        if isinstance(feature, Feature)
    ]

    if len(features) != len(features_from_group):
        for group, feature in features_from_group.items():
            if isinstance(feature, list):
                raise ValueError(
                    f"Feature group {group} doesn't have metadata anywhere"
                )
    return Map(map_name, size_x, size_y, tiles, entities, features)


def _get_tsx(row: int, col: int) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<tileset version="1.10" tiledversion="1.11.2" name="tileset" tilewidth="{TILED_TILE_PIXEL}" tileheight="{TILED_TILE_PIXEL}" tilecount="{row*col}" columns="{col}">
 <image source="tileset.png" width="{TILED_TILE_PIXEL*col}" height="{TILED_TILE_PIXEL*row}"/>
</tileset>
"""


def create_hex_mask(width: int, height: int) -> Image.Image:
    """Create a hexagonal mask for a rectangular tile."""
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    w, h = width, height
    points = [
        (w * 0.5, 0),  # Top
        (w, h * 0.25),  # Top right
        (w, h * 0.75),  # Bottom right
        (w * 0.5, h),  # Bottom
        (0, h * 0.75),  # Bottom left
        (0, h * 0.25),  # Top left
    ]

    draw.polygon(points, fill=255)
    return mask


def gen_tileset_tsx(
    row: int, col: int, old_tileset_image: str = "./tileset.png"
) -> None:
    img = Image.open(old_tileset_image)
    img = img.resize(
        (TILED_TILE_PIXEL * col, TILED_TILE_PIXEL * row), Image.Resampling.LANCZOS
    )
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    alpha = img.getchannel("A")
    hex_mask = create_hex_mask(TILED_TILE_PIXEL, TILED_TILE_PIXEL)
    for y in range(row):
        for x in range(col):
            left = x * TILED_TILE_PIXEL
            top = y * TILED_TILE_PIXEL
            tile_alpha = alpha.crop(
                (left, top, left + TILED_TILE_PIXEL, top + TILED_TILE_PIXEL)
            )
            tile_alpha = ImageChops.multiply(tile_alpha, hex_mask)
            alpha.paste(tile_alpha, (left, top))

    img.putalpha(alpha)
    img.save("tileset.png")
    with Path("./tileset.tsx").open("w+") as f:
        f.write(_get_tsx(row, col))


def reset_toolkit() -> None:
    Path("./tileset.png").unlink(missing_ok=True)
    Path("./rrmap.tsx").unlink(missing_ok=True)
    Path("./rrmap-making-kit.tiled-session").unlink(missing_ok=True)
    with Path("./rrmap.tsx.original").open("r") as original_file:
        with Path("./rrmap.tsx").open("w+") as f:
            f.write(original_file.read())
    with Path("./tileset.tsx").open("w+") as f:
        f.write(_get_tsx(10, 10))
