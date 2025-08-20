from dataclasses import dataclass
from pathlib import Path

from .hexagon import OddRCoord
from .entity import Entity


@dataclass
class Tile:
    coord: OddRCoord
    entities: list[Entity]
    height: int
    image_path: Path
