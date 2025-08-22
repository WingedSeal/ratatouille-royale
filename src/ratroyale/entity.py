from .hexagon import OddRCoord
from typing import TypeVar


class Entity:
    """
    Any entity on the tile system.
    """
    pos: OddRCoord
    health: int | None = None
    defense: int | None = None
    movable: bool = False
    collision: bool = False
    description: str = ""
    height: int = 0

    def __init__(self, pos: OddRCoord) -> None:
        self.pos = pos

    def on_damage_taken(self, damage: int) -> int | None:
        pass

    def on_death(self) -> bool:
        return True

    def take_damage(self, damage: int) -> bool:
        """
        Take damage and reduce health accordingly if entity has health
        :param damage: How much damage taken
        :returns: Whether the entity die
        """
        new_damage = self.on_damage_taken(damage)
        if new_damage is not None:
            damage = new_damage
        if self.health is None:
            return False
        self.health -= max(0, damage - (self.defense or 0))
        if self.health <= 0:
            self.health = 0
            return True
        return False


T = TypeVar('T', bound=Entity)


def entity_data(health: int | None = None,
                defense: int | None = None,
                movable: bool = False,
                collision: bool = False,
                height: int = 0,
                description: str = ""):
    def wrapper(cls: type[T]) -> type[T]:
        assert issubclass(cls, Entity)
        cls.health = health
        cls.defense = defense
        cls.movable = movable
        cls.collision = collision
        cls.description = description
        cls.height = height
        return cls
    return wrapper
