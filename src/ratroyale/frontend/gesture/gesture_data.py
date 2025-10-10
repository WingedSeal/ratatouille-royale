from dataclasses import dataclass
import pygame
from enum import Enum

_BASE = pygame.USEREVENT + 10000


class GestureType(Enum):
    """
    Represents high-level gesture types produced by GestureReader.

    The GestureReader converts raw input events (e.g., mouse or touch events) into these
    higher-level gestures, which are then tagged using this enum.
    """

    CLICK = _BASE + 1
    DRAG_START = _BASE + 2
    DRAG = _BASE + 3
    DRAG_END = _BASE + 4
    SWIPE = _BASE + 5
    HOLD = _BASE + 6
    HOVER = _BASE + 7

    def to_pygame_event(self) -> int:
        return self.value


@dataclass
class GestureData:
    gesture_type: GestureType

    # General attributes common to all gestures.
    mouse_pos: tuple[int, int]
    duration: float

    # Used for N_CLICKS.
    click_count: int = 1

    # Movement-based attributes for DRAG and SWIPE.
    delta: tuple[float, float] | None = None
    direction: tuple[float, float] | None = None
    speed: float | None = None
    start_pos: tuple[int, int] | None = None

    # Attached raw event for pygame_gui down the line.
    # Optional for events that trigger after timeout. (e.g. HOLD)
    raw_event: pygame.event.Event | None = None


def inspect_gesture_events(events: list[pygame.event.Event]) -> None:
    """
    Temporary method for debugging GestureReader.

    Prints when specific high-level gestures occur.
    """
    for e in events:
        if e.type == GestureType.DRAG.value:
            print("Drag initiated")
        elif e.type == GestureType.DRAG_END.value:
            print("Drag released")
        elif e.type == GestureType.HOLD.value:
            print("Hold initiated")
        elif e.type == GestureType.CLICK.value:
            print("Click detected")
        elif e.type == GestureType.SWIPE.value:
            print("Swipe detected")
        elif e.type == GestureType.HOVER.value:
            print("Hover detected")
