from dataclasses import dataclass, field

from .feature import Feature

from .hexagon import OddRCoord
from .entity import Entity


@dataclass
class Tile:
    coord: OddRCoord
    entities: list[Entity]
    height: int
    features: list[Feature] = field(default_factory=list)

    def get_total_height(self) -> int:
        return self.height + max(entity.height for entity in self.entities)
