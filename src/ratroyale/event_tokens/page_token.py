from dataclasses import dataclass
from .base import EventToken
from ratroyale.backend.board import Board
from ratroyale.backend.entity import Entity
from ratroyale.backend.tile import Tile
from ratroyale.input.page_management.page_name import PageName

__all__ = [
    "PageManagerEvent",
    "StartGameConfirmation_PageManagerEvent",
    "EndGame_PageManagerEvent",
    "PauseGame_PageManagerEvent",
    "ResumeGame_PageManagerEvent",
    "EntityInteraction_PageManagerEvent",
    "TileInteraction_PageManagerEvent",
    "EntityMovementConfirmation_PageManagerEvent",
    "EntityAbilityDisplay_PageManagerEvent"
]


@dataclass
class PageManagerEvent(EventToken):
    pass


@dataclass
class StartGameConfirmation_PageManagerEvent(PageManagerEvent):
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

@dataclass
class TileInteraction_PageManagerEvent(PageManagerEvent):
   tile: Tile
   pass

@dataclass 
class EntityMovementConfirmation_PageManagerEvent(PageManagerEvent):
   success: bool
   error_msg: str | None = None

   
   pass

@dataclass
class EntityAbilityDisplay_PageManagerEvent(PageManagerEvent):
   entity: Entity
   pass
