from dataclasses import dataclass
import pygame
from .anim_structure import AnimEvent


# TODO: tentative. may introduce more structure to make this more functional.
@dataclass
class FrameAnim(AnimEvent):
    frame_anim: list[int]
    start_frame: int = 0
    direction: int = 1
    """Determines the direction of the frame animation. \n
    greater than 1 = skips forward (e.g. every other x frame)\n
    1 = normal forward\n
    0 = freeze frame\n
    -1 = normal reversed\n
    less than -1 = skips reversed (e.g. every other x frame)"""

    def __post_init__(self) -> None:
        self._current_index: float = 0.0
