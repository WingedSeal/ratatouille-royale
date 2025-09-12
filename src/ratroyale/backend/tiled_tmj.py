from types import ModuleType
from typing import TYPE_CHECKING, Any
from itertools import count
from .map import Map

try:
    import numpy as np
except ImportError:
    if TYPE_CHECKING:
        import numpy as np


def _get_data_int(layers_data: dict[str, np.typing.NDArray[np.uint8]], layer_name: str) -> list[int]:
    """Supports _e2, _e4, ... suffix"""
    data = layers_data[layer_name]
    for i in count(start=2, step=2):
        if f"{layer_name}_e{i}" not in layers_data:
            break
        data.astype("uint32") += layers_data[f"{layer_name}_e{i}"].astype("uint32")
    return []


def tmj_to_map(tmj_data: dict[str, Any], map_name: str) -> Map:
    import numpy as np
    layers: list[dict[str, Any]] = tmj_data["layers"]
    size_y: int = tmj_data["height"]
    size_x: int = tmj_data["width"]
    layers_data: dict[str, np.typing.NDArray[np.uint8]] = {}
    for layer in layers:
        with np.errstate(over='raise'):
            layers_data[layer["name"]] = np.array(layer["data"], dtype="uint8")

    Map(map_name, size_x, size_y, )
