from dataclasses import dataclass
from enum import Enum, auto

from .base import EventToken
from ratroyale.event_tokens.payloads import Payload

__all__ = [
    "PageManagerEvent",
    "PageNavigation",
    "PageNavigationEvent",
    "PageCallbackEvent",
]


class PageNavigation(Enum):
    """
    Represents high-level navigation commands for managing page transitions
    within the frontend system (e.g. Opening and closing pages)
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


@dataclass
class PageManagerEvent(EventToken):
    pass


@dataclass
class PageNavigationEvent(PageManagerEvent):
    action_list: list[
        tuple[PageNavigation, str | None]
    ]  # List of (action, page_name) tuples


@dataclass
class PageCallbackEvent(PageManagerEvent):
    callback_action: str
    success: bool = True
    error_msg: str | None = None
    payload: Payload | None = None
