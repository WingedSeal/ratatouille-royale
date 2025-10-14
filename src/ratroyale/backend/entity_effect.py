from abc import ABCMeta, abstractmethod
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable, TypeVar

from .side import Side

if TYPE_CHECKING:
    from .entities.rodent import Rodent
    from .entity import Entity
    from .game_manager import GameManager


class EffectMeta(ABCMeta):
    def __call__(cls: "EffectMeta", *args: Any, **kwargs: Any) -> Any:
        if not getattr(cls, "_has_effect_data", False):
            raise TypeError(f"'{cls.__name__}' must be decorated with @effect_subclass")
        return super().__call__(*args, **kwargs)


class EffectClearSide(Enum):
    ENEMY = auto()
    ALLY = auto()
    ANY = auto()
    """Clear on turn of one who goes second"""


class EntityEffect(metaclass=EffectMeta):
    _has_effect_data = False
    name: str
    entity: "Entity"
    duration: int | None
    effect_clear_side: EffectClearSide
    intensity: float
    overridden_effects: list["EntityEffect"]

    def __init__(
        self, entity: "Entity", *, duration: int | None, intensity: float = 0
    ) -> None:
        self.entity = entity
        self.duration = duration
        self.intensity = intensity
        self.overridden_effects = []

    def _should_clear(self, turn: Side) -> bool:
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


def effect_subclass(cls: type[T]) -> type[T]:
    assert issubclass(cls, EntityEffect)
    cls._has_effect_data = True
    return cls


@effect_subclass
class RodentEffect(EntityEffect):
    rodent: "Rodent"

    def __init__(
        self, rodent: "Rodent", *, duration: int | None, intensity: int
    ) -> None:
        self.intensity = intensity
        self.rodent = rodent
        super().__init__(rodent, duration=duration, intensity=intensity)
