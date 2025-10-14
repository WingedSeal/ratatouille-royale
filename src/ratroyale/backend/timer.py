from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable, TypeVar

from .side import Side

if TYPE_CHECKING:
    from .game_manager import GameManager


class Timer(ABC):
    _has_timer_data = False
    duration: int
    timer_clear_side: Side
    intensity: float

    def __init__(self, *, duration: int, intensity: float = 0) -> None:
        if not self._has_timer_data:
            raise TypeError(
                f"'{type(self).__name__}' must be decorated with @timer_data"
            )
        self.duration = duration
        self.intensity = intensity

    def should_clear(self, turn: Side) -> bool:
        return turn == self.timer_clear_side

    @abstractmethod
    def on_turn_change(self, game_manager: "GameManager") -> None: ...

    @abstractmethod
    def on_timer_over(self, game_manager: "GameManager") -> None: ...


T = TypeVar("T", bound=Timer)


def timer_data(timer_clear_side: Side) -> Callable[[type[T]], type[T]]:
    def wrapper(cls: type[T]) -> type[T]:
        assert issubclass(cls, Timer)
        cls._has_timer_data = True
        cls.timer_clear_side = timer_clear_side
        return cls

    return wrapper
