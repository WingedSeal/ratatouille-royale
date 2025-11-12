from abc import abstractmethod
from typing import Callable, TypeVar

from ..entity import Entity, EntitySkill, entity_data
from ..hexagon import OddRCoord
from ..side import Side
from ..tags import EntityTag, RodentClassTag

ENTITY_JUMP_HEIGHT = 1


class Rodent(Entity):
    _has_rodent_data = False
    speed: int
    move_stamina: int
    max_move_stamina: int
    move_cost: int
    attack: int
    class_tag: RodentClassTag
    side: Side | None

    def __init__(self, pos: OddRCoord, side: Side | None = None) -> None:
        if not self._has_rodent_data:
            raise TypeError(
                f"'{type(self).__name__}' must be decorated with @rodent_data(...)"
            )
        super().__init__(pos, side)

    @abstractmethod
    def skill_descriptions(self) -> list[str]: ...

    def reset_stamina(self) -> None:
        self.move_stamina = self.max_move_stamina
        super().reset_stamina()


T = TypeVar("T", bound=type[Rodent])


def rodent_data(
    *,
    name: str,
    speed: int,
    move_stamina: int,
    skill_stamina: int | None,
    move_cost: int,
    attack: int,
    height: int,
    health: int,
    defense: int,
    description: str,
    skills: list[EntitySkill],
    entity_tags: list[EntityTag],
    class_tag: RodentClassTag,
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
            entity_tags=entity_tags,
        )(cls)
        cls._has_rodent_data = True
        cls.health = health
        cls.defense = defense
        cls.description = description
        cls.speed = speed
        cls.move_stamina = move_stamina
        cls.max_move_stamina = move_stamina
        cls.skill_stamina = skill_stamina
        cls.move_cost = move_cost
        cls.attack = attack
        cls.height = height
        cls.movable = movable
        cls.collision = collision
        cls.class_tag = class_tag
        return cls

    return wrapper
