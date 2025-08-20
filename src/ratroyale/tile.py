from dataclasses import dataclass

from .hexagon import OddRCoord
from .entity import Entity


@dataclass
class Tile:
    coord: OddRCoord
    entities: list[Entity]
    height: int
