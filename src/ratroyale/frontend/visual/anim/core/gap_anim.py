from dataclasses import dataclass
from .anim_structure import AnimEvent
from ...asset_management.spritesheet_structure import SpritesheetComponent


@dataclass
class GapAnim(AnimEvent):
    """Does nothing. Used for animation timing purposes."""

    def __post_init__(self) -> None:
        super().__post_init__()

    def update(self, dt: float) -> None:
        self.get_normalized_time(dt)  # still called to advance time
