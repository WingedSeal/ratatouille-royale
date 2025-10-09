from dataclasses import dataclass

from .entity import Entity
from .feature import Feature
from .hexagon import OddRCoord


@dataclass
class GameEvent:
    pass


@dataclass
class EntityMoveEvent(GameEvent):
    path: list[OddRCoord]
    entity: Entity


@dataclass
class EntityDieEvent(GameEvent):
    entity: Entity


@dataclass
class FeatureDieEvent(GameEvent):
    feature: Feature


@dataclass
class EntitySpawnEvent(GameEvent):
    entity: Entity


@dataclass
class EntityDamagedEvent(GameEvent):
    entity: Entity
    damage: int
    hp_loss: int


@dataclass
class FeatureDamagedEvent(GameEvent):
    feature: Feature
    damage: int
    hp_loss: int
