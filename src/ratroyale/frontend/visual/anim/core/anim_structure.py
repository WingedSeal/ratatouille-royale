from dataclasses import dataclass
from typing import Literal, Callable
from abc import ABC, abstractmethod
import math
import pytweening  # type: ignore

# TODO: move all literals into its own enums
TimingMode = Literal["DURATION_PER_LOOP", "DURATION_IN_TOTAL"]


# TODO: reintroduce reverse easing.
@dataclass(kw_only=True)
class AnimEvent(ABC):
    easing_func: Callable[[float], float] = pytweening.linear
    timing_mode: TimingMode
    period: float = 1.0  # in seconds
    reverse_pass_per_loop: bool = False
    compose_with_default: bool = False
    """Will be overridden if part of a GroupedEvent"""
    callback: str | None = None
    loop_count: int | None = 1

    def __post_init__(self) -> None:
        self._elapsed_time: float = 0.0
        self.loop_count = 1 if self.loop_count is None else self.loop_count
        self._current_loop: int = 0
        self._direction: int = 1  # 1 = forward, -1 = reversed
        self._is_finished = False

    def make_callback(self) -> None:
        print("callback triggered")
        pass

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
        if self.timing_mode == "DURATION_PER_LOOP":
            loop_period = self.period
            total_time = (self.loop_count or 1) * loop_period
        elif self.timing_mode == "DURATION_IN_TOTAL":
            loop_period = self.period / (self.loop_count or 1)
            total_time = self.period

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
            return 1.0 if self.reverse_pass_per_loop else 0.0

        # Halves period if ping pong is enabled
        adj_loop_period = loop_period / 2 if self.reverse_pass_per_loop else loop_period

        # Calculate normalized time
        t = (self._elapsed_time / adj_loop_period) % 1

        # Reverse direction on ping pong
        t_mod = self._elapsed_time % loop_period
        reverse = t_mod > adj_loop_period
        self._direction = -1 if reverse else 1

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
    compose_with_default: bool = False
    """If false, this stops default animation. If true, this composes with default."""

    def __post_init__(self) -> None:
        self._current_loop: int = 0

    def update(self, time: float) -> None:
        for anim_event in self.group_list:
            anim_event.update(time)

    def reset(self) -> None:
        pass

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
        pass

    def is_finished(self) -> bool:
        if self._active_anim_index == len(self.sequential_list) - 1:
            return self.sequential_list[self._active_anim_index].is_finished()
        else:
            return False

    def make_callback(self) -> None:
        pass

    def get_animation_group(self) -> GroupedAnim:
        return self.sequential_list[self._active_anim_index]
