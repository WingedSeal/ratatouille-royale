from .skill_callback import SkillCallback
from .side import Side
from .hexagon import OddRCoord
import inspect
from typing import TYPE_CHECKING, Callable, TypeVar, cast

from dataclasses import asdict, dataclass

if TYPE_CHECKING:
    from .game_manager import GameManager


@dataclass(kw_only=True)
class _EntitySkill:
    name: str
    method_name: str
    reach: int | None
    crumb_cost: int
    altitude: int | None


@dataclass
class SkillResult:
    target_count: int
    available_targets: list[OddRCoord]
    callback: SkillCallback


@dataclass
class EntitySkill(_EntitySkill):
    func: Callable[["GameManager"], SkillResult | None]


MINIMAL_DAMAGE_TAKEN = 1


class Entity:
    """
    Any entity on the tile system.
    """
    pos: OddRCoord
    name: str = ""
    max_health: int | None = None
    health: int | None = None
    defense: int | None = None
    movable: bool = False
    collision: bool = False
    description: str = ""
    height: int = 0
    skills: list[EntitySkill] = []
    side: Side | None

    def __init__(self, pos: OddRCoord, side: Side | None = None) -> None:
        self.pos = pos
        self.side = side

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
        damage_taken = max(MINIMAL_DAMAGE_TAKEN, damage - (self.defense or 0))
        self.health -= damage_taken
        if self.health <= 0:
            damage_taken += self.health
            self.health = 0
            self.on_hp_loss(damage_taken)
            return True, damage_taken
        self.on_hp_loss(damage_taken)
        return False, damage_taken


Entity_T = TypeVar('Entity_T', bound=Entity)


def entity_data(*,
                health: int | None = None,
                defense: int | None = None,
                movable: bool = False,
                collision: bool = False,
                height: int = 0,
                description: str = "",
                skills: list[_EntitySkill] = [],
                name: str = ""
                ):
    def wrapper(cls: type[Entity_T]) -> type[Entity_T]:
        assert issubclass(cls, Entity)
        cls.health = health
        cls.max_health = health
        cls.defense = defense
        cls.movable = movable
        cls.collision = collision
        cls.description = description
        cls.height = height
        cls.name = name
        for skill in skills:
            if not hasattr(cls, skill.method_name):
                raise ValueError(
                    f"{skill} is not an attribute of {cls.__name__}")
            skill_function = getattr(cls, skill.method_name)
            if not callable(skill_function):
                raise ValueError(
                    f"{skill} is not callable")
            arg_count = len(inspect.signature(skill_function).parameters)
            if arg_count != 1:
                raise ValueError(
                    f"Expected {skill} method to take 1 arguments (got {arg_count})"
                )
            cls.skills.append(EntitySkill(
                **asdict(skill), func=cast(Callable[["GameManager"], SkillResult | None], skill_function)))
        return cls
    return wrapper


_entity_skill_type = Callable[[Entity_T, "GameManager"], SkillResult | None]


def entity_skill_check(method: _entity_skill_type) -> _entity_skill_type:
    """
    Decorator for validating skill method signature
    """
    return method
