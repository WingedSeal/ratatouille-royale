from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import TYPE_CHECKING, Callable, TypeVar

from .side import Side

if TYPE_CHECKING:
    from .entity import Entity
    from .game_manager import GameManager


class EffectClearSide(Enum):
    ENEMY = auto()
    ALLY = auto()
    ANY = auto()
    """Clear on turn of one who goes second"""


class EntityEffect(ABC):
    _has_effect_data = False
    name: str
    entity: "Entity"
    duration: int | None
    turn_passed: int
    effect_clear_side: EffectClearSide
    intensity: float
    overridden_effects: list["EntityEffect"]

    def __init__(
        self, entity: "Entity", *, duration: int | None, intensity: float = 0
    ) -> None:
        if not self._has_effect_data:
            raise TypeError(
                f"'{type(self).__name__}' must be decorated with @effect_data"
            )
        self.entity = entity
        self.duration = duration
        self.turn_passed = 0
        self.intensity = intensity
        self.overridden_effects = []

    def should_clear(self, turn: Side) -> bool:
        match self.effect_clear_side:
            case EffectClearSide.ENEMY:
                side = self.entity.side
                if side is None:
                    raise ValueError(
                        "Can't clear effect on enemy turn since its entity has no side"
                    )
                return turn == side.other_side()
            case EffectClearSide.ALLY:
                side = self.entity.side
                if side is None:
                    raise ValueError(
                        "Can't clear effect on ally turn since its entity has no side"
                    )
                return turn == side
            case EffectClearSide.ANY:
                return True

    @abstractmethod
    def on_turn_change(self, game_manager: "GameManager") -> None: ...

    @abstractmethod
    def on_applied(
        self, game_manager: "GameManager", *, is_overriding: bool
    ) -> None: ...

    @abstractmethod
    def on_cleared(
        self, game_manager: "GameManager", *, is_overridden: bool
    ) -> None: ...

    @abstractmethod
    def effect_descriptions(self) -> str: ...


T = TypeVar("T", bound=EntityEffect)


def effect_data(
    effect_clear_side: EffectClearSide, *, name: str
) -> Callable[[type[T]], type[T]]:
    def wrapper(cls: type[T]) -> type[T]:
        assert issubclass(cls, EntityEffect)
        cls._has_effect_data = True
        cls.effect_clear_side = effect_clear_side
        cls.name = name
        return cls

    return wrapper
