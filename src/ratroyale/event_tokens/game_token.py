from dataclasses import dataclass
from .base import EventToken
from ratroyale.backend.tile import Tile
from ratroyale.backend.entity import Entity
from .game_action import GameAction
from typing import TypeVar, Generic

__all__ = [
  "GameManagerEvent"
]

T = TypeVar("T")

@dataclass
class GameManagerEvent(Generic[T], EventToken):
    game_action: GameAction
    payload: T | None = None


# @dataclass
# class RequestStartGame(GameManagerEvent):
#     map_path: str | None = (
#         None  # Could change to enums that represents different premade stages later.
#     )
#     pass


# @dataclass
# class CardPlacement_GameManagerEvent(GameManagerEvent):
#   pass

# @dataclass
# class RequestEntityMovement_GameManagerEvent(GameManagerEvent):
#   entity: Entity
#   tile: Tile
