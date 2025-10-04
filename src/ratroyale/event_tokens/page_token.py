from dataclasses import dataclass
from .base import EventToken
from ratroyale.backend.board import Board
from ratroyale.backend.entity import Entity
from ratroyale.backend.tile import Tile
from enum import Enum as enum, auto
from typing import TYPE_CHECKING

__all__ = [
    "PageManagerEvent",
    "PageNavigation",
    "PageNavigationEvent",
    "PageTargetedEvent",

    "StartGameConfirmation",
    "EntityInteraction_PageManagerEvent",
    "TileInteraction_PageManagerEvent",
    "EntityMovementConfirmation_PageManagerEvent",
    "EntityAbilityDisplay_PageManagerEvent"
]

class PageNavigation(enum):
    PUSH = auto()
    POP = auto()
    REMOVE = auto()
    REPLACE = auto()
    HIDE = auto()
    SHOW = auto()
    REMOVE_ALL = auto()

@dataclass
class PageManagerEvent(EventToken):
    ...

@dataclass
class PageNavigationEvent(PageManagerEvent):
    action_list: list[tuple[PageNavigation, str | None]]  # List of (action, page_name) tuples

@dataclass
class PageTargetedEvent(PageManagerEvent):
    page_name: str

@dataclass
class StartGameConfirmation(PageTargetedEvent):
   board: Board | None

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
