from dataclasses import dataclass
from .base import EventToken
from ratroyale.input.page_management.page_name import PageName

__all__ = [
  "GameManagerEvent",
  "RequestStart_GameManagerEvent",
  "CardPlacement_GameManagerEvent"
]

@dataclass
class GameManagerEvent(EventToken):
  page_name: PageName
  pass

@dataclass
class RequestStart_GameManagerEvent(GameManagerEvent):
  map_path: str | None = None # Could change to enums that represents different premade stages later.
  pass

@dataclass
class CardPlacement_GameManagerEvent(GameManagerEvent):
  pass