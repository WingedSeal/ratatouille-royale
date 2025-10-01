from dataclasses import dataclass
from .base import EventToken
from ratroyale.input.constants import PageName
from ratroyale.backend.board import Board

__all__ = [
    "PageManagerEvent",
    "AddPageEvent_PageManagerEvent",
    "RemovePageEvent_PageManagerEvent",
    "ReplaceTopPage_PageManagerEvent",
    "ConfirmStartGame_PageManagerEvent",
    "EndGame_PageManagerEvent",
]


@dataclass
class PageManagerEvent(EventToken):
    pass


@dataclass
class AddPageEvent_PageManagerEvent(PageManagerEvent):
    page_name: PageName


@dataclass
class RemovePageEvent_PageManagerEvent(PageManagerEvent):
    page_name: PageName | None = None


@dataclass
class ReplaceTopPage_PageManagerEvent(PageManagerEvent):
    page_name: PageName


@dataclass
class ConfirmStartGame_PageManagerEvent(PageManagerEvent):
    board: Board | None


@dataclass
class EndGame_PageManagerEvent(PageManagerEvent):
    pass
