from dataclasses import dataclass
from .base import EventToken
from ratroyale.input.page_management.page_name import PageName
from ratroyale.backend.tile import Tile
from ratroyale.backend.entity import Entity

__all__ = [
  "GameManagerEvent",
  "RequestStart_GameManagerEvent",
  "CardPlacement_GameManagerEvent",
  "TryEntityMovement_GameManagerEvent"
]

@dataclass
class GameManagerEvent(EventToken):
  pass

@dataclass
class RequestStart_GameManagerEvent(GameManagerEvent):
  map_path: str | None = None # Could change to enums that represents different premade stages later.
  pass

@dataclass
class CardPlacement_GameManagerEvent(GameManagerEvent):
  pass

@dataclass
class TryEntityMovement_GameManagerEvent(GameManagerEvent):
  entity: Entity
  tile: Tile