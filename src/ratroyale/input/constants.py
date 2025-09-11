from enum import Enum, auto


class ActionKey(Enum):
  # Canvas actions
  SELECT_TILE = auto()
  SELECT_UNIT = auto()

  # UI actions
  START_GAME = auto()
  BACK_TO_MENU = auto()
  QUIT = auto()
  PAUSE_GAME = auto()
  RESUME_GAME = auto()


class GestureKey(Enum):
  # Gesture actions
  CLICK = auto()
  DOUBLE_CLICK = auto()
  DRAG = auto()
  DRAG_END = auto()
  SWIPE = auto()
  HOLD = auto()
  SCROLL = auto()

class GUIEventSource(Enum):
  UI_ELEMENT = auto()
  GESTURE = auto()

# Enum for page names
class PageName(Enum):
    MAIN_MENU = auto()
    TEST_SWAP = auto()
    GAME_BOARD = auto()
    CARD_OVERLAY = auto()
    PAUSE_BUTTON = auto()
    PAUSE_MENU = auto()


