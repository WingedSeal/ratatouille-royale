from enum import Enum, auto

# gui_event_constants.py
from pygame_gui import UI_BUTTON_PRESSED, UI_BUTTON_DOUBLE_CLICKED, UI_BUTTON_START_PRESS, UI_BUTTON_ON_HOVERED, UI_BUTTON_ON_UNHOVERED
from pygame_gui import UI_TEXT_ENTRY_FINISHED, UI_TEXT_ENTRY_CHANGED
from pygame_gui import UI_CHECK_BOX_CHECKED, UI_CHECK_BOX_UNCHECKED
from pygame_gui import UI_DROP_DOWN_MENU_CHANGED

from pygame_gui.elements import UIButton, UITextEntryLine, UISelectionList

class StrEnum(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name

class ActionKey(StrEnum):
  # Canvas actions
  CANVAS = auto()

  # UI actions
  START_GAME = auto()
  BACK_TO_MENU = auto()
  QUIT = auto()

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

class PageEventAction(StrEnum):
  ADD = auto()
  REMOVE = auto()
  REPLACE_TOP = auto()

# Enum for page names
class PageName(StrEnum):
    MAIN_MENU = auto()
    TEST_SWAP = auto()
    BOARD = auto()

CONSUMED_UI_EVENTS = {
    UI_BUTTON_PRESSED,
    UI_BUTTON_DOUBLE_CLICKED,
    UI_BUTTON_START_PRESS,
    UI_TEXT_ENTRY_FINISHED,
    UI_TEXT_ENTRY_CHANGED,
    UI_CHECK_BOX_CHECKED,
    UI_CHECK_BOX_UNCHECKED,
    UI_DROP_DOWN_MENU_CHANGED,
    UI_BUTTON_ON_HOVERED,
    UI_BUTTON_ON_UNHOVERED,
    # etc.
}

# Set/tuple of widget types that should fully consume events
UI_WIDGETS_ALWAYS_CONSUMING = (
   UIButton, 
   UITextEntryLine, 
   UISelectionList
   )
