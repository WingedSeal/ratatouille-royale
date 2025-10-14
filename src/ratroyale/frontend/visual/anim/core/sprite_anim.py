from dataclasses import dataclass
from .anim_structure import AnimEvent
from ...asset_management.spritesheet_structure import SpritesheetComponent
from ...asset_management.spritesheet_manager import SpritesheetManager


@dataclass
class SpriteAnim(AnimEvent):
    spritesheet_component: SpritesheetComponent
    animation_name: str
    start_frame: int = 0
    start_direction: int = 1
    """Determines the direction of the frame animation.
    >1 = skip frames forward
    1 = normal forward
    0 = freeze frame
    -1 = normal reversed
    <-1 = skip frames reversed
    """

    def __post_init__(self) -> None:
        super().__post_init__()
        self._current_frame: int = self.start_frame
        self._direction: int = self.start_direction
        self._frame_count: int = SpritesheetManager.get_frame_count(
            self.spritesheet_component.get_key(), self.animation_name
        )

    def update(self, time_delta: float) -> None:
        """Advance the frame animation according to elapsed time, easing, and direction."""
        # Get normalized time (0–1) and loop completion info
        eased_t = self.get_normalized_time(time_delta)

        # Determine frame progression
        total_frames = self._frame_count
        frame_index = int(eased_t * (total_frames - 1))

        # Apply direction and start offset
        frame_index = (
            self.start_frame + frame_index * abs(self._direction)
        ) % total_frames
        if self._direction < 0:
            frame_index = total_frames - 1 - frame_index

        # Update the spritesheet
        self.spritesheet_component.set_frame(self.animation_name, frame_index)
        self._current_frame = frame_index
