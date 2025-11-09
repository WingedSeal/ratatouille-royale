from dataclasses import dataclass

from .base import EventToken
from enum import Enum, auto


# TODO: figure the visual domain out more concretely.
class PageVisual(Enum):
    """
    Represents high-level events for controlling page visibility, layering,
    and input reception within the frontend system.
    """

    HIDE = auto()
    """Temporarily hide a page without removing it from the stack."""
    SHOW = auto()
    """Restore a previously hidden page."""
    MOVE_DOWN = auto()
    """Move a page lower in the visual stacking order."""
    MOVE_UP = auto()
    """Move a page higher in the visual stacking order."""
    STOP_INPUT = auto()
    """Stop input on a given page."""
    STOP_INPUT_ALL = auto()
    """Stop input for all pages. No page name argument required."""
    RESUME_INPUT = auto()
    """Resume input on a given page."""
    RESUME_INPUT_ALL = auto()
    """Resume input for all pages. No page name argument required."""


@dataclass
class VisualManagerEvent(EventToken):
    page_name: str
    callback_action: str
