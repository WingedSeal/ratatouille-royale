from enum import Enum, auto


class ActionKey(Enum):
  # Game actions
  SELECT_TILE = auto()
  SELECT_UNIT = auto()

  # Navigation actions
  START_GAME = auto()
  BACK_TO_MENU = auto()
  QUIT = auto()
  PAUSE_GAME = auto()
  RESUME_GAME = auto()


class GestureKey(Enum):
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

class PageName(Enum):
    MAIN_MENU = auto()
    TEST_SWAP = auto()
    GAME_BOARD = auto()
    CARD_OVERLAY = auto()
    PAUSE_BUTTON = auto()
    PAUSE_MENU = auto()


