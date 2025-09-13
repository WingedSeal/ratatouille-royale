from dataclasses import dataclass, field

from .side import Side
from .feature import Feature
from .hexagon import OddRCoord
from .entity import Entity


@dataclass
class Tile:
    coord: OddRCoord
    height: int
    entities: list[Entity] = field(default_factory=list)
    features: list[Feature] = field(default_factory=list)

    def get_total_height(self, turn: Side | None) -> int:
        return self.height + max((entity.height for entity in self.entities if entity.side != turn), default=0)
