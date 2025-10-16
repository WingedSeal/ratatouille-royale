from dataclasses import dataclass
from .anim_structure import AnimEvent


@dataclass
class GapAnim(AnimEvent):
    """Introduces a time gap where no animation happens. Used for animation timing purposes."""

    def __post_init__(self) -> None:
        super().__post_init__()

    def update(self, time_delta: float) -> None:
        self.get_normalized_time(time_delta)  # still called to advance time
