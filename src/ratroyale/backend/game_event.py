from dataclasses import dataclass

from .hexagon import OddRCoord
from .entity import Entity


@dataclass
class GameEvent:
    pass


@dataclass
class EntityMoveEvent(GameEvent):
    move_from: OddRCoord
    move_to: OddRCoord
    entity: Entity


@dataclass
class EntityDieEvent(GameEvent):
    entity: Entity
