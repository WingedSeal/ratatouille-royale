from abc import ABCMeta, abstractmethod
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, TypeVar
from .side import Side
if TYPE_CHECKING:
    from entity import Entity


class EffectMeta(ABCMeta):
    def __new__(cls, name: str, bases: tuple[type, ...], dct: dict[str, Any]):
        if bases and not dct.get("_has_effect_data", False):
            raise TypeError(
                f"'{name}' must be decorated with @effect_data(...)")
        return super().__new__(cls, name, bases, dct)


class EffectClearSide(Enum):
    ENEMY = auto()
    ALLY = auto()
    ANY = auto()
    """Clear on turn of one who goes second"""


class EntityEffect(metaclass=EffectMeta):
    _has_effect_data = False
    entity: "Entity"
    duration: int | None
    max_duration: int | None
    effect_clear_side: EffectClearSide

    def __init__(self, entity: "Entity", *, duration: int | None) -> None:
        self.entity = entity
        self.duration = duration
        self.max_duration = duration

    def _should_clear(self, turn: Side) -> bool:
        match self.effect_clear_side:
            case EffectClearSide.ENEMY:
                side = self.entity.side
                if side is None:
                    raise ValueError(
                        "Can't clear effect on enemy turn since its entity has no side")
                return turn == side.other_side()
            case EffectClearSide.ALLY:
                side = self.entity.side
                if side is None:
                    raise ValueError(
                        "Can't clear effect on enemy turn since its entity has no side")
                return turn == side
            case EffectClearSide.ANY:
                return True

    @abstractmethod
    def on_turn_change(self, turn_count_before_change: int, turn_before_change: Side):
        ...

    @abstractmethod
    def on_applied(self):
        ...

    @abstractmethod
    def on_cleared(self):
        ...

    @abstractmethod
    def effect_descriptions(self) -> list[str]:
        ...


T = TypeVar('T', bound=EntityEffect)


def effect_data(effect_clear_side: EffectClearSide):
    def wrapper(cls: type[T]) -> type[T]:
        assert issubclass(cls, EntityEffect)
        cls._has_effect_data = True
        cls.effect_clear_side = effect_clear_side
        return cls
    return wrapper
