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
  DOUBLE_CLICK = auto()
  DRAG = auto()
  DRAG_END = auto()
  SWIPE = auto()
  HOLD = auto()

@dataclass
class GestureData:
    gesture_type: GestureType

    start_pos: tuple[int, int] | None = None
    end_pos: tuple[int, int] | None = None
    current_pos: tuple[int, int] | None = None
    delta: tuple[int, int] | None = None
    duration: float | None = None
    velocity: tuple[float, float] | None = None
    mouse: str | None = None # Supposed to represent which mouse is held. (left, right, or scrollwheel). Currently unused

    original_event: pygame.event.Event | None = None

CLICK_EVENT: int = pygame.USEREVENT + 40000
DOUBLE_CLICK_EVENT: int = pygame.USEREVENT + 40001
DRAG_EVENT: int = pygame.USEREVENT + 40002
DRAG_END_EVENT: int = pygame.USEREVENT + 40003
SWIPE_EVENT: int = pygame.USEREVENT + 40004
HOLD_EVENT: int = pygame.USEREVENT + 40005

GESTURE_EVENT_MAP: dict[GestureType, int] = {
  GestureType.CLICK: CLICK_EVENT,
  GestureType.DOUBLE_CLICK: DOUBLE_CLICK_EVENT,
  GestureType.DRAG: DRAG_EVENT,
  GestureType.DRAG_END: DRAG_END_EVENT,
  GestureType.SWIPE: SWIPE_EVENT,
  GestureType.HOLD: HOLD_EVENT
}

def to_event(gesture_type: GestureType) -> int:
   return GESTURE_EVENT_MAP[gesture_type]