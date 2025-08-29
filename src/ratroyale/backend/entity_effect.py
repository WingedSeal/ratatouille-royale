from abc import ABCMeta, abstractmethod
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


class EntityEffect(metaclass=EffectMeta):
    _has_effect_data = False
    entity: "Entity"
    duration: int | None
    max_duration: int | None
    clear_turn: Side | None

    def __init__(self, entity: "Entity") -> None:
        self.entity = entity

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


def effect_data(*, duration: int | None, clear_turn: Side | None):
    def wrapper(cls: type[T]) -> type[T]:
        assert issubclass(cls, EntityEffect)
        cls._has_effect_data = True
        cls.duration = duration
        cls.max_duration = duration
        cls.clear_turn = clear_turn
        return cls
    return wrapper
