from dataclasses import dataclass
from ratroyale.input.gesture_management.gesture_type import GestureType
import pygame

@dataclass
class GestureData:
    gesture_key: GestureType

    start_pos: tuple[int, int] | None = None
    end_pos: tuple[int, int] | None = None
    current_pos: tuple[int, int] | None = None
    delta: tuple[int, int] | None = None
    duration: float | None = None
    velocity: tuple[float, float] | None = None
    key: str | None = None
    mouse: str | None = None
    scroll_amount: int | None = None
    raw_event: pygame.event.Event | None = None