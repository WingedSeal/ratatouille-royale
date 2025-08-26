from dataclasses import dataclass

from .hexagon import OddRCoord
from .entity import Entity


@dataclass
class Tile:
    coord: OddRCoord
    entities: list[Entity]
    height: int

    def get_total_height(self) -> int:
        return self.height + max(entity.height for entity in self.entities)
