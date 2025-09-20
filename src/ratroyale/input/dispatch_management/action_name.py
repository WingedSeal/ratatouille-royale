from enum import Enum, auto

class ActionName(Enum):
  # Game actions
  SELECT_TILE = auto()
  SELECT_UNIT = auto()

  # Navigation actions
  START_GAME = auto()
  BACK_TO_MENU = auto()
  QUIT = auto()
  PAUSE_GAME = auto()
  RESUME_GAME = auto()


