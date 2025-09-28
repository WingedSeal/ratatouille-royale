from enum import Enum, auto

class ActionName(Enum):
  # Game actions
  HOVER_TILE = auto()
  HOVER_UNIT = auto()
  SELECT_TILE = auto()
  SELECT_UNIT = auto()
  DISPLAY_ABILITY_MENU = auto()
  SELECT_ABILITY = auto()

  # Navigation actions
  START_GAME = auto()
  BACK_TO_MENU = auto()
  QUIT = auto()
  PAUSE_GAME = auto()
  RESUME_GAME = auto()


