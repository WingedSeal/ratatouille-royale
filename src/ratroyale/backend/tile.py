from dataclasses import dataclass, field
from pprint import pformat

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

    def __repr__(self) -> str:
        return f"""Tile(
    coord={repr(self.coord)}, 
    height={self.height},
    entities={pformat(self.entities)},
    features={pformat(self.features)}
)"""

    def __str__(self) -> str:
        return f"Tile(height={self.height})"
