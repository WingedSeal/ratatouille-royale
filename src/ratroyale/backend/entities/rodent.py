from abc import ABCMeta, abstractmethod
from ..entity import Entity, entity_data
from ..hexagon import OddRCoord
from ..entity import _EntitySkill
from typing import Any, Callable, TypeVar
from ..side import Side


ENTITY_JUMP_HEIGHT = 1


class Rodent(Entity):
    _has_rodent_data = False
    speed: int
    stamina: int
    move_cost: int
    attack: int
    side: Side | None

    def __init__(self, pos: OddRCoord, side: Side | None = None) -> None:
        if not self._has_rodent_data:
            raise TypeError(
                f"'{type(self).__name__}' must be decorated with @rodent_data(...)"
            )
        super().__init__(pos, side)

    @abstractmethod
    def skill_descriptions(self) -> list[str]: ...


T = TypeVar("T", bound=type[Rodent])


def rodent_data(
    *,
    name: str,
    speed: int,
    stamina: int,
    move_cost: int,
    attack: int,
    height: int,
    health: int,
    defense: int,
    description: str,
    skills: list[_EntitySkill],
    movable: bool = True,
    collision: bool = True,
) -> Callable[[T], T]:
    def wrapper(cls: T) -> T:
        assert issubclass(cls, Rodent)
        entity_data(
            health=health,
            defense=defense,
            movable=movable,
            collision=collision,
            height=height,
            description=description,
            skills=skills,
            name=name,
        )(cls)
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
