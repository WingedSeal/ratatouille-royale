from dataclasses import dataclass
from .base import EventToken
from ratroyale.backend.board import Board
from ratroyale.backend.entity import Entity
from ratroyale.input.page_management.page_name import PageName

__all__ = [
    "PageManagerEvent",
    "ConfirmStartGame_PageManagerEvent",
    "EndGame_PageManagerEvent",
    "PauseGame_PageManagerEvent",
    "ResumeGame_PageManagerEvent",
    "EntityInteraction_PageManagerEvent"
]

@dataclass
class PageManagerEvent(EventToken):
  page_name: PageName
  pass

@dataclass
class ConfirmStartGame_PageManagerEvent(PageManagerEvent):
   board: Board | None

@dataclass 
class EndGame_PageManagerEvent(PageManagerEvent):
   pass

@dataclass
class PauseGame_PageManagerEvent(PageManagerEvent):
   pass

@dataclass 
class ResumeGame_PageManagerEvent(PageManagerEvent):
    pass

@dataclass
class EntityInteraction_PageManagerEvent(PageManagerEvent):
   entity: Entity
   pass
