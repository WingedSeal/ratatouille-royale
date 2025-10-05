from dataclasses import dataclass
from .base import EventToken
from ratroyale.backend.board import Board
from ratroyale.backend.entity import Entity
from ratroyale.backend.tile import Tile
from .game_action import GameAction
from enum import Enum, auto
from typing import TypeVar, Generic

T = TypeVar("T")

__all__ = [
    "PageManagerEvent",
    "PageNavigation",
    "PageNavigationEvent",
    "PageCallbackEvent"
]

class PageNavigation(Enum):
    OPEN = auto()
    CLOSE = auto()
    CLOSE_TOP = auto()
    REPLACE_TOP = auto()
    CLOSE_ALL = auto()
    HIDE = auto()
    SHOW = auto()

@dataclass
class PageManagerEvent(EventToken):
    pass

@dataclass
class PageNavigationEvent(PageManagerEvent):
    action_list: list[tuple[PageNavigation, str | None]]  # List of (action, page_name) tuples

@dataclass
class PageCallbackEvent(Generic[T], PageManagerEvent):
    page_list: list[str]
    game_action: GameAction
    success: bool = True
    error_msg: str | None = None
    payload: T | None = None

# @dataclass
# class StartGameConfirmation(PageQueryResponseEvent):
#    board: Board | None = None

# @dataclass
# class EntityInteraction_PageManagerEvent(PageManagerEvent):
#    entity: Entity
#    pass

# @dataclass
# class TileInteraction_PageManagerEvent(PageManagerEvent):
#    tile: Tile
#    pass

# @dataclass 
# class EntityMovementConfirmation_PageManagerEvent(PageManagerEvent):
#    success: bool
#    error_msg: str | None = None

   
#    pass

# @dataclass
# class EntityAbilityDisplay_PageManagerEvent(PageManagerEvent):
#    entity: Entity
#    pass
