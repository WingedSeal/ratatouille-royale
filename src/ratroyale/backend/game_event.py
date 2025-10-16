from dataclasses import dataclass
from typing import Literal

from ratroyale.backend.damage_heal_source import DamageHealSource

from .player_info.squeak import Squeak
from .instant_kill import InstantKill
from .entity import Entity
from .entity_effect import EffectClearSide, EntityEffect
from .feature import Feature
from .hexagon import OddRCoord
from .side import Side

STR_PREFIX = "Event: "
_PRINT_EVENTS = False


def damage_heal_source_to_string(damage_heal_source: DamageHealSource) -> str:
    if isinstance(damage_heal_source, Entity):
        return f"{damage_heal_source.name} at {damage_heal_source.pos}"
    elif isinstance(damage_heal_source, EntityEffect):
        return f"{damage_heal_source.name} effect"
    elif isinstance(damage_heal_source, Feature):
        return f"Feature {damage_heal_source.__class__.__name__} around {damage_heal_source.shape[0]}"
    elif damage_heal_source is None:
        return "unknown source"


@dataclass
class GameEvent:
    def __post_init__(self) -> None:
        if _PRINT_EVENTS:
            print(self)


@dataclass
class EntityMoveEvent(GameEvent):
    path: list[OddRCoord]
    entity: Entity

    def __str__(self) -> str:
        return f"{STR_PREFIX}{self.entity.name} at {self.entity.pos} was moved to {self.path[-1]}."


@dataclass
class EntityDieEvent(GameEvent):
    entity: Entity

    def __str__(self) -> str:
        return f"{STR_PREFIX}{self.entity.name} at {self.entity.pos} died."


@dataclass
class FeatureDieEvent(GameEvent):
    feature: Feature

    def __str__(self) -> str:
        return f"{STR_PREFIX}Feature {self.feature.__class__.__name__} around {self.feature.shape[0]} died."


@dataclass
class EntitySpawnEvent(GameEvent):
    entity: Entity

    def __str__(self) -> str:
        return f"{STR_PREFIX}{self.entity.name} spawned at {self.entity.pos}."


@dataclass
class EntityDamagedEvent(GameEvent):
    entity: Entity
    damage: int | InstantKill
    hp_loss: int
    source: DamageHealSource

    def __str__(self) -> str:
        if isinstance(self.damage, InstantKill):
            return f"{STR_PREFIX}{self.entity.name} at {self.entity.pos} took instant kill damage from {damage_heal_source_to_string(self.source)} losing all its remaining hp ({self.hp_loss}). HP Remaining: {self.entity.health}"
        return f"{STR_PREFIX}{self.entity.name} at {self.entity.pos} took {self.damage} damage from {damage_heal_source_to_string(self.source)} losing {self.hp_loss} hp. HP Remaining: {self.entity.health}"


@dataclass
class EntityHealedEvent(GameEvent):
    entity: Entity
    heal: int
    hp_gained: int
    overheal_cap: int
    source: DamageHealSource

    def __str__(self) -> str:
        if (
            self.entity.health
            and self.entity.max_health
            and self.entity.health > self.entity.max_health
        ):
            overheal_message = (
                f" and now has {self.entity.health - self.entity.max_health} overheal."
            )
        else:
            overheal_message = "."
        if self.entity is self.source:
            return f"{STR_PREFIX}{self.entity.name} at {self.entity.pos} healed {self.heal} hp from itself gaining {self.hp_gained} hp{overheal_message} HP Remaining: {self.entity.health}"
        return f"{STR_PREFIX}{self.entity.name} at {self.entity.pos} healed {self.heal} hp from {damage_heal_source_to_string(self.source)} gaining {self.hp_gained} hp{overheal_message} HP Remaining: {self.entity.health}"


@dataclass
class FeatureDamagedEvent(GameEvent):
    feature: Feature
    damage: int
    hp_loss: int
    source: DamageHealSource

    def __str__(self) -> str:
        return f"{STR_PREFIX}Feature {self.feature.__class__.__name__} around {self.feature.shape[0]} took {self.damage} damage from {damage_heal_source_to_string(self.source)} losing {self.hp_loss} hp HP Remaining: {self.feature.health}"


@dataclass
class EndTurnEvent(GameEvent):
    is_from_first_turn_side: bool
    from_side: Side
    to_side: Side
    leftover_crumbs: int
    new_crumbs: int

    def __str__(self) -> str:
        return f"{STR_PREFIX}Changing turn from player {'1' if self.is_from_first_turn_side else '2'} to player {'2' if self.is_from_first_turn_side else '1'}. New crumbs: {self.new_crumbs}"


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

    def __str__(self) -> str:
        if self.apply_or_clear == "apply":
            apply_or_clear = "applied"
        elif self.apply_or_clear == "clear":
            apply_or_clear = "cleared"
        else:
            raise NotImplementedError()
        match self.effect.effect_clear_side:
            case EffectClearSide.ALLY:
                clear_side = " of ally"
            case EffectClearSide.ENEMY:
                clear_side = " of enemy"
            case EffectClearSide.ANY:
                clear_side = ""
        return f"{STR_PREFIX}{self.effect.entity.name} at {self.effect.entity.pos} has effect {self.effect.name} {apply_or_clear} with intensity of {self.effect.intensity} for {self.effect.duration}{clear_side} turn(s). Reason: {self.reason}"


@dataclass
class GameOverEvent(GameEvent):
    is_winner_from_first_turn_side: bool
    victory_side: Side

    def __str__(self) -> str:
        return f"{STR_PREFIX}Game Over! Player {'1' if self.is_winner_from_first_turn_side else '2'} won."


@dataclass
class SqueakPlacedEvent(GameEvent):
    hand_index: int
    squeak: Squeak
    coord: OddRCoord

    def __str__(self) -> str:
        return f"{STR_PREFIX}Squeak {self.squeak.name} (slot {self.hand_index}) placed at {self.coord}"


@dataclass
class SqueakDrawnEvent(GameEvent):
    hand_index: int
    squeak: Squeak

    def __str__(self) -> str:
        return f"{STR_PREFIX}Squeak {self.squeak.name} was drawn into slot {self.hand_index}"


@dataclass
class SqueakSetResetEvent(GameEvent):

    def __str__(self) -> str:
        return f"{STR_PREFIX}Squeak set has been reset"
