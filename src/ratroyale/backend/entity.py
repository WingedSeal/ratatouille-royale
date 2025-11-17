import inspect
from dataclasses import asdict, dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, Callable, ClassVar, TypeAlias, TypeVar, cast


from .entity_effect import EntityEffect
from .hexagon import OddRCoord
from .instant_kill import InstantKill
from .side import Side
from .skill_callback import SkillCallback
from .source_of_damage_or_heal import SourceOfDamageOrHeal
from .tags import EntityTag, SkillTag

if TYPE_CHECKING:
    from .game_manager import GameManager
    from .feature import Feature
    from .board import Board


@dataclass(kw_only=True, frozen=True)
class EntitySkill:
    name: str
    method_name: str
    reach: int | None
    crumb_cost: int
    altitude: int | None
    tags: list[SkillTag]


@dataclass(frozen=True)
class SkillTargeting:
    target_count: int
    source_enitity: "Entity"
    source_skill: "CallableEntitySkill"
    available_targets: list[OddRCoord]
    _callback: SkillCallback
    can_cancel: bool


class SkillCompleted(Enum):
    SUCCESS = auto()
    CANCELLED = auto()


SkillResult: TypeAlias = SkillTargeting | SkillCompleted


@dataclass(frozen=True)
class CallableEntitySkill(EntitySkill):
    func: Callable[["Entity", "GameManager"], SkillResult]


MINIMAL_DAMAGE_TAKEN = 1


class Entity:
    """
    Any entity on the tile system.
    """

    pos: OddRCoord
    effects: dict[str, EntityEffect]
    """Dictionary of its effect name and its effect"""
    name: str
    max_health: int | None
    health: int | None
    defense: int
    movable: bool
    skill_stamina: int | None
    max_skill_stamina: int | None
    entity_tags: list[EntityTag]
    collision: bool
    description: str
    height: int
    side: Side | None
    skills: list[CallableEntitySkill]
    is_dead: bool
    PRE_PLACED_ENTITIES: ClassVar[dict[int, type["Entity"]]] = {}
    """Map of preplaced-able entities' IDs to the entity class"""

    @classmethod
    def PRE_PLACED_ENTITY_ID(cls) -> int | None:
        """Non-zero positive integer representing entity's ID for preplacing it during map generation. Can be `None` if it cannot be preplaced."""
        return None

    def __init_subclass__(cls) -> None:
        entity_id = cls.PRE_PLACED_ENTITY_ID()
        if entity_id is None:
            return
        if entity_id in Entity.PRE_PLACED_ENTITIES:
            raise Exception(
                f"{cls.__name__} and {Entity.PRE_PLACED_ENTITIES[entity_id]} both have the same preplaced entity ID ({entity_id})"
            )
        Entity.PRE_PLACED_ENTITIES[entity_id] = cls

    def __init__(self, pos: OddRCoord, side: Side | None = None) -> None:
        self.pos = pos
        self.side = side
        self.effects = {}
        self.is_dead = False

    def on_damage_taken(
        self,
        game_manager: "GameManager",
        damage: int | InstantKill,
        source: SourceOfDamageOrHeal,
    ) -> int | None:
        pass

    def on_summon(self, game_manager: "GameManager") -> None:
        pass

    def on_spawn(self, board: "Board") -> None:
        pass

    def on_hp_loss(
        self, game_manager: "GameManager", hp_loss: int, source: SourceOfDamageOrHeal
    ) -> None:
        pass

    def on_hp_gain(
        self, game_manager: "GameManager", hp_gain: int, source: SourceOfDamageOrHeal
    ) -> None:
        pass

    def on_heal(
        self, game_manager: "GameManager", heal: int, source: SourceOfDamageOrHeal
    ) -> int | None:
        pass

    def on_ally_move(
        self,
        game_manager: "GameManager",
        ally: "Entity",
        path: list[OddRCoord],
        origin: OddRCoord,
    ) -> None: ...

    def on_enemy_move(
        self,
        game_manager: "GameManager",
        enemy: "Entity",
        path: list[OddRCoord],
        origin: OddRCoord,
    ) -> None: ...

    def on_turn_change(
        self, game_manager: "GameManager", turn_change_to: Side
    ) -> (
        None
    ): ...  # This has to be `...` to avoid having GameManager running on_turn_change on every entity. It'll detect the ellipsis to cache them.

    def on_kill_entity(
        self, game_manager: "GameManager", target_killed: "Entity"
    ) -> None:
        pass

    def on_kill_feature(
        self, game_manager: "GameManager", target_killed: "Feature"
    ) -> None:
        pass

    def reset_stamina(self) -> None:
        self.skill_stamina = self.max_skill_stamina

    def on_death(self, source: SourceOfDamageOrHeal) -> bool:
        """
        Method called when entity dies
        :returns: Whether the entity actually dies
        """
        return True

    def passive_descriptions(self) -> list[tuple[str, str]]:
        return []

    def _heal(
        self,
        game_manager: "GameManager",
        heal: int,
        source: SourceOfDamageOrHeal,
        overheal_cap: int = 0,
    ) -> int:
        """
        Heal and increase health accordingly if entity has health
        :returns: How much it actually healed
        """
        new_heal = self.on_heal(game_manager, heal, source)
        if new_heal is not None:
            heal = new_heal
        if self.health is None or self.max_health is None:
            raise ValueError("Entity without health just got healed")
        heal_taken = min(self.max_health + overheal_cap - self.health, heal)
        self.health += heal_taken
        self.on_hp_gain(game_manager, heal_taken, source)
        return heal_taken

    def _take_damage(
        self,
        game_manager: "GameManager",
        damage: int | InstantKill,
        source: SourceOfDamageOrHeal,
    ) -> tuple[bool, int]:
        """
        Take damage and reduce health accordingly if entity has health
        :param damage: How much damage taken
        :returns: Whether the entity die and hp loss
        """
        if isinstance(damage, InstantKill):
            self.on_damage_taken(game_manager, damage, source)
            self.on_hp_loss(game_manager, self.health or 0, source)
            return True, self.health or 0
        new_damage = self.on_damage_taken(game_manager, damage, source)
        if new_damage is not None:
            damage = new_damage
        if self.health is None:
            raise ValueError("Entity without health just taken damage")
        damage_taken = max(MINIMAL_DAMAGE_TAKEN, damage - max(self.defense, 0))
        self.health -= damage_taken
        if self.health <= 0:
            damage_taken += self.health
            self.health = 0
            self.is_dead = True
            self.on_hp_loss(game_manager, damage_taken, source)
            return True, damage_taken
        self.on_hp_loss(game_manager, damage_taken, source)
        return False, damage_taken

    def __repr__(self) -> str:
        return f"Entity({self.pos!r}, {self.side!r})"

    def __str__(self) -> str:
        return self.name


Entity_T = TypeVar("Entity_T", bound=Entity)


def entity_data(
    *,
    health: int | None = None,
    defense: int = 0,
    skill_stamina: int | None = None,
    movable: bool = False,
    collision: bool = False,
    height: int = 0,
    entity_tags: list[EntityTag] = [],
    description: str = "",
    skills: list[EntitySkill] = [],
    name: str = "",
) -> Callable[[type[Entity_T]], type[Entity_T]]:
    def wrapper(cls: type[Entity_T]) -> type[Entity_T]:
        assert issubclass(cls, Entity)
        cls.health = health
        cls.max_health = health
        cls.defense = defense
        cls.skill_stamina = skill_stamina
        cls.max_skill_stamina = skill_stamina
        cls.movable = movable
        cls.collision = collision
        cls.description = description
        cls.height = height
        cls.name = name
        cls.entity_tags = entity_tags
        cls.skills = []
        for skill in skills:
            if not hasattr(cls, skill.method_name):
                raise ValueError(f"{skill} is not an attribute of {cls.__name__}")
            skill_function = getattr(cls, skill.method_name)
            if not callable(skill_function):
                raise ValueError(f"{skill} is not callable")
            arg_count = len(inspect.signature(skill_function).parameters)
            if arg_count != 2:
                raise ValueError(
                    f"Expected {skill} method to take 2 arguments (got {arg_count - 1})"
                )
            cls.skills.append(
                CallableEntitySkill(
                    **asdict(skill),
                    func=cast(
                        Callable[[Entity, "GameManager"], SkillResult],
                        skill_function,
                    ),
                )
            )
        return cls

    return wrapper


_entity_skill_type = Callable[[Entity_T, "GameManager"], SkillResult]


def entity_skill_check(
    method: _entity_skill_type[Entity_T],
) -> _entity_skill_type[Entity_T]:
    """
    Decorator for validating skill method signature
    """
    return method
