from abc import abstractmethod
from .entity_effect import EntityEffect
from .skill_callback import SkillCallback
from .side import Side
from .hexagon import OddRCoord
import inspect
from typing import TYPE_CHECKING, Callable, ClassVar, TypeVar, cast

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
    can_cancel: bool


@dataclass
class EntitySkill(_EntitySkill):
    func: Callable[["GameManager"], SkillResult | None]


MINIMAL_DAMAGE_TAKEN = 1


class Entity:
    """
    Any entity on the tile system.
    """
    pos: OddRCoord
    effects: dict[str, EntityEffect]
    name: str = ""
    max_health: int | None = None
    health: int | None = None
    defense: int = 0
    movable: bool = False
    collision: bool = False
    description: str = ""
    height: int = 0
    skills: list[EntitySkill] = []
    side: Side | None
    PRE_PLACED_ENTITIES: ClassVar[dict[int, type["Entity"]]] = {}

    @classmethod
    def PRE_PLACED_ENTITY_ID(cls) -> int | None:
        return None

    def __init_subclass__(cls) -> None:
        entity_id = cls.PRE_PLACED_ENTITY_ID()
        if entity_id is None:
            return
        if entity_id in Entity.PRE_PLACED_ENTITIES:
            raise Exception(
                f"{cls.__name__} and {Entity.PRE_PLACED_ENTITIES[entity_id]} both have the same preplaced entity ID ({entity_id})")
        Entity.PRE_PLACED_ENTITIES[entity_id] = cls

    def __init__(self, pos: OddRCoord, side: Side | None = None) -> None:
        self.pos = pos
        self.side = side
        self.effects = {}

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
        damage_taken = max(MINIMAL_DAMAGE_TAKEN, damage - self.defense)
        self.health -= damage_taken
        if self.health <= 0:
            damage_taken += self.health
            self.health = 0
            self.on_hp_loss(damage_taken)
            return True, damage_taken
        self.on_hp_loss(damage_taken)
        return False, damage_taken

    def __repr__(self) -> str:
        return f"Entity({self.pos!r}, {self.side!r})"

    def __str__(self) -> str:
        return self.name


Entity_T = TypeVar('Entity_T', bound=Entity)


def entity_data(*,
                health: int | None = None,
                defense: int = 0,
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
            if arg_count != 2:
                raise ValueError(
                    f"Expected {skill} method to take 1 arguments (got {arg_count - 1})"
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
