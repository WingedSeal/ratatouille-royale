from enum import Enum, auto

# gui_event_constants.py
class StrEnum(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name

class ActionKey(StrEnum):
  # Canvas actions
  SELECT_TILE = auto()
  SELECT_UNIT = auto()

  # UI actions
  START_GAME = auto()
  BACK_TO_MENU = auto()
  QUIT = auto()
  PAUSE_GAME = auto()
  RESUME_GAME = auto()


class GestureKey(StrEnum):
  # Gesture actions
  CLICK = auto()
  DOUBLE_CLICK = auto()
  DRAG = auto()
  DRAG_END = auto()
  SWIPE = auto()
  HOLD = auto()
  SCROLL = auto()

class GUIEventSource(StrEnum):
  UI_ELEMENT = auto()
  GESTURE = auto()

# Enum for page names
class PageName(StrEnum):
    MAIN_MENU = auto()
    TEST_SWAP = auto()
    GAME_BOARD = auto()
    CARD_OVERLAY = auto()
    PAUSE_BUTTON = auto()
    PAUSE_MENU = auto()


