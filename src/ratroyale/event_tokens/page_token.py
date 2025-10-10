from dataclasses import dataclass
from .base import EventToken
from enum import Enum, auto

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
    current page stack, such as opening new pages, closing existing ones, hiding/showing pages, or
    reordering their display priority.
    """

    OPEN = auto()
    """Open a new page on top of the current page stack."""
    CLOSE = auto()
    """Close the active page with a given name."""
    CLOSE_TOP = auto()
    """Close the topmost page. No page name argument required."""
    REPLACE_TOP = auto()
    """Replace the current top page with a new one."""
    CLOSE_ALL = auto()
    """Close all pages in the stack, returning to an empty state. No page name argument required."""
    HIDE = auto()
    """Temporarily hide a page without removing it from the stack."""
    SHOW = auto()
    """Restore a previously hidden page."""
    MOVE_DOWN = auto()
    """Move a page lower in the visual stacking order."""
    MOVE_UP = auto()
    """Move a page higher in the visual stacking order."""


@dataclass
class PageManagerEvent(EventToken):
    pass


@dataclass
class PageNavigationEvent(PageManagerEvent):
    action_list: list[
        tuple[PageNavigation, str | None]
    ]  # List of (action, page_name) tuples


@dataclass
class PageCallbackEvent[T](PageManagerEvent):
    callback_action: str
    success: bool = True
    error_msg: str | None = None
    payload: T | None = None
