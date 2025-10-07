from dataclasses import dataclass
from .base import EventToken
from ratroyale.backend.board import Board
from ratroyale.backend.entity import Entity
from ratroyale.backend.tile import Tile
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
    callback_action: str
    success: bool = True
    error_msg: str | None = None
    payload: T | None = None
