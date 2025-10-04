from dataclasses import dataclass
from .base import EventToken
from ratroyale.backend.tile import Tile
from ratroyale.backend.entity import Entity

__all__ = [
  "GameManagerEvent",
  "RequestStart_GameManagerEvent",
  "CardPlacement_GameManagerEvent",
  "RequestEntityMovement_GameManagerEvent"
]


@dataclass
class GameManagerEvent(EventToken):
    pass


@dataclass
class RequestStart_GameManagerEvent(GameManagerEvent):
    map_path: str | None = (
        None  # Could change to enums that represents different premade stages later.
    )
    pass


@dataclass
class CardPlacement_GameManagerEvent(GameManagerEvent):
  pass

@dataclass
class RequestEntityMovement_GameManagerEvent(GameManagerEvent):
  entity: Entity
  tile: Tile
