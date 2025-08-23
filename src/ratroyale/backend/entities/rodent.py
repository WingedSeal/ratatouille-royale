from abc import ABCMeta, abstractmethod
from ..entity import Entity, entity_data
from ..hexagon import OddRCoord
from ..entity import _EntitySkill
from typing import TYPE_CHECKING, Any,  TypeVar

if TYPE_CHECKING:
    from ..side import Side


class RodentMeta(ABCMeta):
    def __new__(cls, name: str, bases: tuple[type, ...], dct: dict[str, Any]):
        if bases and not dct.get("_has_rodent_data", False):
            raise TypeError(
                f"'{name}' must be decorated with @rodent_data(...)")
        return super().__new__(cls, name, bases, dct)


RODENT_JUMP_HEIGHT = 1


class Rodent(Entity, metaclass=RodentMeta):
    _has_rodent_data = False
    speed: int
    stamina: int
    move_cost: int
    attack: int
    side: Side

    def __init__(self, pos: OddRCoord, side: Side) -> None:
        super().__init__(pos)
        self.side = side

    @abstractmethod
    def skill_descriptions(self) -> list[str]:
        ...


T = TypeVar('T', bound=Rodent)


def rodent_data(*,
                speed: int,
                stamina: int,
                move_cost: int,
                attack: int,
                height: int,
                health: int | None = None,
                defense: int | None = None,
                movable: bool = True,
                collision: bool = True,
                description: str = "",
                skills: list[_EntitySkill] = [],
                ):
    def wrapper(cls: type[T]) -> type[T]:
        assert issubclass(cls, Rodent)
        entity_data(health, defense, movable, collision,
                    height, description, skills)(cls)
        cls._has_rodent_data = True
        cls.health = health
        cls.defense = defense
        cls.description = description
        cls.speed = speed
        cls.stamina = stamina
        cls.move_cost = move_cost
        cls.attack = attack
        cls.height = height
        cls.movable = movable
        cls.collision = collision
        return cls
    return wrapper
