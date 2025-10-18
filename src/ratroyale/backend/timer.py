from enum import Enum, auto
from typing import TYPE_CHECKING, Protocol, TypeVar

from .side import Side

if TYPE_CHECKING:
    from .entity import Entity
    from .game_manager import GameManager


class TimerClearSide(Enum):
    ENEMY = auto()
    ALLY = auto()
    ANY = auto()
    """Clear on turn of one who goes second"""


class TimerCallback(Protocol):
    def __call__(self, timer: "Timer", game_manager: "GameManager") -> None: ...


def empty_timer_callback(timer: "Timer", game_manager: "GameManager") -> None:
    pass


class Timer:
    _has_timer_data = False
    duration: int
    timer_clear_side: TimerClearSide
    on_timer_over: TimerCallback
    on_turn_change: TimerCallback

    def __init__(
        self,
        entity: "Entity",
        timer_clear_side: TimerClearSide,
        *,
        on_turn_change: TimerCallback | None,
        on_timer_over: TimerCallback | None,
        duration: int,
    ) -> None:
        self.timer_clear_side = timer_clear_side
        self.duration = duration
        self.entity = entity
        if on_turn_change is not None:
            self.on_turn_change = on_turn_change
        else:
            self.on_turn_change = empty_timer_callback
        if on_timer_over is not None:
            self.on_timer_over = on_timer_over
        else:
            self.on_timer_over = empty_timer_callback

    def should_clear(self, turn: Side) -> bool:
        match self.timer_clear_side:
            case TimerClearSide.ENEMY:
                side = self.entity.side
                if side is None:
                    raise ValueError(
                        "Can't clear timer on enemy turn since its entity has no side"
                    )
                return turn == side.other_side()
            case TimerClearSide.ALLY:
                side = self.entity.side
                if side is None:
                    raise ValueError(
                        "Can't clear timer on ally turn since its entity has no side"
                    )
                return turn == side
            case TimerClearSide.ANY:
                return True


T = TypeVar("T", bound=Timer)
