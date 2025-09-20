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
  SCROLL = auto()

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