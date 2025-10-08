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
    "PageCallbackEvent",
]


class PageNavigation(Enum):
    """
    Represents high-level navigation commands for managing page transitions
    within the frontend system.

    Each value describes an action that the PageManager can perform on the
    current page stack, such as opening new pages, closing existing ones, or
    reordering their display priority.

    Members
    --------
    OPEN
        Push a new page on top of the current page stack.
    CLOSE
        Close the active page with a given name.
    CLOSE_TOP
        Close the topmost page. No page name argument required.
    REPLACE_TOP
        Replace the current top page with a new one.
    CLOSE_ALL
        Close all pages in the stack, returning to an empty state. No page name argument required.
    HIDE
        Temporarily hide a page without removing it from the stack.
    SHOW
        Restore a previously hidden page.
    BRING_DOWN
        Move a page lower in the visual stacking order.
    BRING_UP
        Move a page higher in the visual stacking order.
    """

    OPEN = auto()
    CLOSE = auto()
    CLOSE_TOP = auto()
    REPLACE_TOP = auto()
    CLOSE_ALL = auto()
    HIDE = auto()
    SHOW = auto()
    BRING_DOWN = auto()
    BRING_UP = auto()


@dataclass
class PageManagerEvent(EventToken):
    pass


@dataclass
class PageNavigationEvent(PageManagerEvent):
    action_list: list[
        tuple[PageNavigation, str | None]
    ]  # List of (action, page_name) tuples


@dataclass
class PageCallbackEvent(Generic[T], PageManagerEvent):
    callback_action: str
    success: bool = True
    error_msg: str | None = None
    payload: T | None = None
