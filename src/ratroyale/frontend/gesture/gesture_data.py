from dataclasses import dataclass
import pygame
from enum import Enum, auto


class GestureType(Enum):
    """
    Represents high-level gesture types produced by GestureReader.

    The GestureReader converts raw input events (e.g., mouse or touch events) into these
    higher-level gestures, which are then tagged using this enum.
    """

    CLICK = auto()
    DRAG_START = auto()
    DRAG = auto()
    DRAG_END = auto()
    SWIPE = auto()
    HOLD = auto()
    HOVER = auto()


_OFFSET_CONSTANT = 10000
_BASE = pygame.USEREVENT + _OFFSET_CONSTANT

# Value doesn't matter. What matters is that our chosen values don't overlap
# with pygame or pygame_gui's own events.
CLICK_EVENT: int = _BASE + 1
DRAG_START_EVENT: int = _BASE + 8
DRAG_EVENT: int = _BASE + 3
DRAG_END_EVENT: int = _BASE + 4
SWIPE_EVENT: int = _BASE + 5
HOLD_EVENT: int = _BASE + 6
HOVER_EVENT: int = _BASE + 7

GESTURE_EVENT_MAP: dict[GestureType, int] = {
    GestureType.CLICK: CLICK_EVENT,
    GestureType.DRAG_START: DRAG_START_EVENT,
    GestureType.DRAG: DRAG_EVENT,
    GestureType.DRAG_END: DRAG_END_EVENT,
    GestureType.SWIPE: SWIPE_EVENT,
    GestureType.HOLD: HOLD_EVENT,
    GestureType.HOVER: HOVER_EVENT,
}


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


def to_event(gesture_type: GestureType) -> int:
    return GESTURE_EVENT_MAP[gesture_type]


def inspect_gesture_events(events: list[pygame.event.Event]) -> None:
    """
    Temporary method for debugging GestureReader.

    Prints when specific high-level gestures occur.
    """
    for e in events:
        if e.type == to_event(GestureType.DRAG):
            print("Drag initiated")
        elif e.type == to_event(GestureType.DRAG_END):
            print("Drag released")
        elif e.type == to_event(GestureType.HOLD):
            print("Hold initiated")
        elif e.type == to_event(GestureType.CLICK):
            print("Click detected")
        elif e.type == to_event(GestureType.SWIPE):
            print("Swipe detected")
        elif e.type == to_event(GestureType.HOVER):
            print("Hover detected")
