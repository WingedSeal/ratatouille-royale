from dataclasses import dataclass
from typing import Callable
from abc import ABC, abstractmethod
import math
import pytweening  # type: ignore
from .anim_settings import TimingMode, AnimDirection
from .....event_tokens.visual_token import VisualManagerEvent
from .....coordination_manager import CoordinationManager


@dataclass(kw_only=True)
class AnimEvent(ABC):
    easing_func: Callable[[float], float] = pytweening.linear
    timing_mode: TimingMode
    period_in_seconds: float = 1.0
    reverse_pass_per_loop: bool = False
    run_together_with_default: bool = False
    """Will be overridden if part of a GroupedEvent"""
    callback: str | None = None
    loop_count: int | None = 1

    def __post_init__(self) -> None:
        self._elapsed_time: float = 0.0
        self.loop_count = 1 if self.loop_count is None else self.loop_count
        self._current_loop: int = 0
        self._direction: AnimDirection = AnimDirection.FORWARD
        self._is_finished = False

    def make_callback(self) -> None:
        """
        Called when an animation loop completes.
        If 'callback' is set, dispatch it as a VisualManagerEvent.
        """
        if self.callback is None:
            return

        event = VisualManagerEvent(callback=self.callback)
        CoordinationManager.put_message(event)

    def reset(self) -> None:
        self._current_loop = 0
        self._elapsed_time = 0.0
        self._is_finished = False

    def is_finished(self) -> bool:
        return self._is_finished

    def get_normalized_time(self, time_delta: float) -> float:
        """
        Update elapsed time, respecting timing mode, reversal, and loop structure.
        Returns normalized_t
        """
        # Determine timing mode.
        if self.timing_mode == TimingMode.DURATION_PER_LOOP:
            loop_period = self.period_in_seconds
            total_time = (self.loop_count or 1) * loop_period
        elif self.timing_mode == TimingMode.DURATION_IN_TOTAL:
            loop_period = self.period_in_seconds / (self.loop_count or 1)
            total_time = self.period_in_seconds

        # Record previous time & updated time.
        prev_time = self._elapsed_time
        self._elapsed_time += time_delta

        # If elapsed time crosses loop period threshold, fire callbacks.
        callback_count = math.floor(self._elapsed_time / loop_period) - math.floor(
            prev_time / loop_period
        )
        for i in range(0, callback_count):
            self.make_callback()

        # If elapsed time is already over total time, stop animation by passing an unchanging normalized time.
        if self._elapsed_time >= total_time:
            self._elapsed_time = total_time
            self._is_finished = True
            return 1.0

        # Halves period if ping pong is enabled
        adj_loop_period = loop_period / 2 if self.reverse_pass_per_loop else loop_period

        # Calculate normalized time
        t = (self._elapsed_time / adj_loop_period) % 1

        # Reverse direction on ping pong
        t_mod = self._elapsed_time % loop_period
        reverse = t_mod > adj_loop_period
        self._direction = AnimDirection.REVERSE if reverse else AnimDirection.FORWARD

        return self.easing_func(t)

    @abstractmethod
    def update(self, time: float) -> None: ...


@dataclass
class GroupedAnim:
    group_list: list[AnimEvent]
    callback: str | None = None
    """A callback happens once all animations in the list is finished."""
    loop_count: int = 1
    """Replays the animation for this amount of time."""
    run_together_with_default: bool = False
    """If false, this stops default animation. If true, this composes with default."""

    def __post_init__(self) -> None:
        self._current_loop: int = 0

    def update(self, time: float) -> None:
        for anim_event in self.group_list:
            anim_event.update(time)

    def reset(self) -> None:
        self._current_loop += 1
        for anim in self.group_list:
            anim.reset()

    def is_finished(self) -> bool:
        for anim_event in self.group_list:
            if not anim_event.is_finished():
                return False
        else:
            return True

    def make_callback(self) -> None:
        pass


@dataclass
class SequentialAnim:
    """A SequentialAnim object holds a sequence of GroupedAnims (animations to be executed together)."""

    sequential_list: list[GroupedAnim]
    callback: str | None = None
    """A callback happens once all animations in the sequence is finished."""
    loop_count: int = 1
    """Replays the animation for this amount of time."""
    persistent: bool = False
    """If true, this animation does not leave the queue once it is finished."""
    interrupts_queue: bool = False
    """If true, all other SequentialAnims in the sequence gets removed."""

    def __post_init__(self) -> None:
        self._active_anim_index: int = 0
        self._current_loop: int = 0

    def update(self, time: float) -> None:
        self.get_animation_group().update(time)

    def reset(self) -> None:
        self._active_anim_index = 0
        self._current_loop += 1
        for anim in self.sequential_list:
            anim.reset()

    def is_finished(self) -> bool:
        if self._active_anim_index == len(self.sequential_list) - 1:
            return self.sequential_list[self._active_anim_index].is_finished()
        else:
            return False

    def make_callback(self) -> None:
        pass

    def get_animation_group(self) -> GroupedAnim:
        return self.sequential_list[self._active_anim_index]

    def run_together_with_default(self) -> bool:
        return self.get_animation_group().run_together_with_default
