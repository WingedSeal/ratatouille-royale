from abc import ABC, abstractmethod
from dataclasses import dataclass
from pprint import pformat
from typing import ClassVar, Iterable

from .hexagon import OddRCoord
from .side import Side

MINIMAL_FEATURE_DAMAGE_TAKEN = 1


@dataclass
class Feature(ABC):
    shape: list[OddRCoord]
    health: int | None = None
    defense: int = 0
    side: Side | None = None
    ALL_FEATURES: ClassVar[dict[int, type["Feature"]]] = {}
    """Map of all features' IDs to the feature class"""

    @staticmethod
    @abstractmethod
    def FEATURE_ID() -> int:
        """Non-zero positive integer representing feature's ID unique to each feature class"""
        ...

    @staticmethod
    @abstractmethod
    def is_collision() -> bool: ...

    def __init_subclass__(cls) -> None:
        if cls.FEATURE_ID() in Feature.ALL_FEATURES:
            raise Exception(
                f"{cls.__name__} and {Feature.ALL_FEATURES[cls.FEATURE_ID()]} both have the same feature ID ({cls.FEATURE_ID()})"
            )
        Feature.ALL_FEATURES[cls.FEATURE_ID()] = cls

    def on_damage_taken(self, damage: int) -> int | None:
        pass

    def on_hp_loss(self, hp_loss: int) -> None:
        pass

    def on_death(self) -> bool:
        """
        Method called when entity dies
        :returns: Whether the entity actually dies
        """
        return True

    def _take_damage(self, damage: int) -> tuple[bool, int]:
        """
        Take damage and reduce health accordingly if entity has health
        :param damage: How much damage taken
        :returns: Whether the entity die and hp loss
        """
        new_damage = self.on_damage_taken(damage)
        if new_damage is not None:
            damage = new_damage
        if self.health is None:
            raise ValueError("Entity without health just taken damage")
        damage_taken = max(MINIMAL_FEATURE_DAMAGE_TAKEN, damage - self.defense)
        self.health -= damage_taken
        if self.health <= 0:
            damage_taken += self.health
            self.health = 0
            self.on_hp_loss(damage_taken)
            return True, damage_taken
        self.on_hp_loss(damage_taken)
        return False, damage_taken

    def __repr__(self) -> str:
        return f"""Feature(
    shape={pformat(self.shape)},
    health={self.health},
    defense={self.defense},
    side={self.side},
)"""
