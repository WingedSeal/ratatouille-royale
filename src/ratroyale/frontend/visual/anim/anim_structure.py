from dataclasses import dataclass
import pygame
from typing import Literal, Callable

TimingMode = Literal["DURATION", "SPEED"]


@dataclass
class AnimEvent:
    easing_func: Callable[[float], float]
    timing_mode: TimingMode
    time: float

    def __post_init__(self) -> None:
        self._elapsed_time: float = 0.0

    def update(self, surface: pygame.Surface, time: float) -> None:
        pass

    def reset(self) -> None:
        pass

    def is_finished(self) -> bool:
        return True

    def compute_rect(self, rect: pygame.Rect) -> pygame.Rect:
        return pygame.Rect()

    def make_callback(self) -> None:
        pass


@dataclass
class GroupedAnim:
    group_list: list[AnimEvent]
    callback: str | None = None
    """A callback happens once all animations in the list is finished."""
    loop_count: int = 1
    """Replays the animation for this amount of time."""

    def update(self, surface: pygame.Surface, time: float) -> None:
        pass

    def reset(self) -> None:
        pass

    def is_finished(self) -> bool:
        return True

    def compute_rect(self, rect: pygame.Rect) -> pygame.Rect:
        return pygame.Rect()

    def make_callback(self) -> None:
        pass


@dataclass
class SequentialAnim:
    """A SequentialAnim object holds a sequence of GroupedAnims (animations to be executed together)."""

    sequential_list: list[GroupedAnim | AnimEvent]
    callback: str | None = None
    """A callback happens once all animations in the sequence is finished."""
    is_persistent: bool = False
    """If marked true, this animation does not leave the queue once it is finished."""
    loop_count: int = 1
    """Replays the animation for this amount of time."""

    def update(self, surface: pygame.Surface, time: float) -> None:
        pass

    def reset(self) -> None:
        pass

    def is_finished(self) -> bool:
        return True

    def compute_rect(self, rect: pygame.Rect) -> pygame.Rect:
        return pygame.Rect()

    def make_callback(self) -> None:
        pass
