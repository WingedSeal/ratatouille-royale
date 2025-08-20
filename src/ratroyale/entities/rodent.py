from abc import ABCMeta, abstractmethod
import inspect
from dataclasses import asdict, dataclass
from ..entity import Entity
from ..hexagon import OddRCoord
from typing import Any, Callable, TypeVar, cast


class RodentMeta(ABCMeta):
    def __new__(cls, name: str, bases: tuple[type, ...], dct: dict[str, Any]):
        if bases and not dct.get("_has_rodent_data", False):
            raise TypeError(
                f"'{name}' must be decorated with @rodent_data(...)")
        return super().__new__(cls, name, bases, dct)


@dataclass
class _RodentSkill:
    method_name: str
    reach: int
    crumb_cost: int


@dataclass
class RodentSkill(_RodentSkill):
    func: Callable[[], None]


class Rodent(Entity, metaclass=RodentMeta):
    _has_rodent_data = False
    skills: list[RodentSkill] = []
    speed: int
    stamina: int
    move_cost: int
    attack: int
    height: int

    def __init__(self, pos: OddRCoord) -> None:
        super().__init__(pos)

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
                skills: list[_RodentSkill] = [],
                ):
    def wrapper(cls: type[T]) -> type[T]:
        assert issubclass(cls, Rodent)
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
        for skill in skills:
            if not hasattr(cls, skill.method_name):
                raise ValueError(
                    f"{skill} is not an attribute of {cls.__name__}")
            skill_function = getattr(cls, skill.method_name)
            if not callable(skill_function):
                raise ValueError(
                    f"{skill} is not callable")
            arg_count = len(inspect.signature(skill_function).parameters)
            if arg_count != 0:
                raise ValueError(
                    f"Expected {skill} method to take 0 arguments (got {arg_count})"
                )
            cls.skills.append(RodentSkill(
                **asdict(skill), func=cast(Callable[[], None], skill_function)))
        return cls
    return wrapper
