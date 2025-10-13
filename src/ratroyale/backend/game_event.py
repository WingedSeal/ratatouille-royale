from dataclasses import dataclass
from typing import Literal

from .entity_effect import EntityEffect
from .side import Side
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


@dataclass
class EndTurnEvent(GameEvent):
    from_side: Side
    to_side: Side
    leftover_crumbs: int
    new_crumbs: int


@dataclass
class EntityEffectUpdateEvent(GameEvent):
    effect: EntityEffect
    apply_or_clear: Literal["apply", "clear"]
    reason: Literal[
        "overriding",
        "overriden",
        "normal_apply",
        "force_clear",
        "duration_over",
        "duration_over_and_replaced_by_weaker_effect",
        "replacing_stronger_effect_that_duration_over",
    ]


@dataclass
class GameOverEvent(GameEvent):
    victory_side: Side
