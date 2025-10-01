from types import ModuleType
from typing import TYPE_CHECKING, Any
from itertools import count
from .map import Map

try:
    import numpy as np
except ImportError:
    if TYPE_CHECKING:
        import numpy as np


def _get_data_int(layers_data: dict[str, np.typing.NDArray[np.uint8]], layer_name: str) -> np.typing.NDArray[np.uint32]:
    """Supports _e2, _e4, ... suffix"""
    data = layers_data[layer_name]
    big_data: np.typing.NDArray[np.uint32] = data.astype("uint32")
    for i in count(start=2, step=2):
        if f"{layer_name}_e{i}" not in layers_data:
            break
        big_data += layers_data[f"{layer_name}_e{i}"].astype(
            "uint32") * (10 ** i)
    return big_data


def tmj_to_map(tmj_data: dict[str, Any], map_name: str) -> Map:
    layers: list[dict[str, Any]] = tmj_data["layers"]
    size_y: int = tmj_data["height"]
    size_x: int = tmj_data["width"]
    layers_data: dict[str, np.typing.NDArray[np.uint8]] = {}
    for layer in layers:
        with np.errstate(over='raise'):
            layers_data[layer["name"]] = np.array(layer["data"], dtype="uint8")
    tiles_data = np.hstack([
        _get_data_int(layers_data, "id"),
        _get_data_int(layers_data, "height")
    ])

    Map(map_name, size_x, size_y, [])
