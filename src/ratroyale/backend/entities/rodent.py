from abc import ABCMeta, abstractmethod
from ..entity import Entity, entity_data
from ..hexagon import OddRCoord
from ..entity import _EntitySkill
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from ..side import Side


class RodentMeta(ABCMeta):
    def __call__(cls, *args, **kwargs):
        if not getattr(cls, '_has_rodent_data', False):
            raise TypeError(
                f"'{cls.__name__}' must be decorated with @rodent_data(...)")
        return super().__call__(*args, **kwargs)


ENTITY_JUMP_HEIGHT = 1


class Rodent(Entity, metaclass=RodentMeta):
    _has_rodent_data = False
    speed: int
    stamina: int
    move_cost: int
    attack: int
    side: Side | None

    def __init__(self, pos: OddRCoord, side: Side | None = None) -> None:
        super().__init__(pos, side)

    @abstractmethod
    def skill_descriptions(self) -> list[str]:
        ...


T = TypeVar('T', bound=Rodent)


def rodent_data(*,
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
                ):
    def wrapper(cls: type[T]) -> type[T]:
        assert issubclass(cls, Rodent)
        entity_data(
            health=health,
            defense=defense,
            movable=movable,
            collision=collision,
            height=height,
            description=description,
            skills=skills,
            name=name)(cls)
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
