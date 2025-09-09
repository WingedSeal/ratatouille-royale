from dataclasses import dataclass
from typing import Iterable
from .side import Side
from .hexagon import OddRCoord


MINIMAL_FEATURE_DAMAGE_TAKEN = 1


@dataclass
class Feature:
    shape: list[OddRCoord]
    health: int | None = None
    defense: int | None = None
    side: Side | None = None

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
        damage_taken = max(MINIMAL_FEATURE_DAMAGE_TAKEN,
                           damage - (self.defense or 0))
        self.health -= damage_taken
        if self.health <= 0:
            damage_taken += self.health
            self.health = 0
            self.on_hp_loss(damage_taken)
            return True, damage_taken
        self.on_hp_loss(damage_taken)
        return False, damage_taken
