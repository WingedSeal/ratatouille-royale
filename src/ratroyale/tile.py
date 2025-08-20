from dataclasses import dataclass
from enum import Enum, auto

from .hexagon import OddRCoord
from .entity import Entity


class TileModifier(Enum):
    ON_FIRE = auto()


@dataclass
class Tile:
    coord: OddRCoord
    entities: list[Entity]
    modifiers: list[TileModifier]
    height: int
