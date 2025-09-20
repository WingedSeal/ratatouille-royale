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