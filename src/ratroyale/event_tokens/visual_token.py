from __future__ import annotations
from dataclasses import dataclass
from .base import EventToken
from ratroyale.visual.asset_management.visual_component import VisualComponent
from ratroyale.input.page_management.interactable import Interactable
from pygame_gui.ui_manager import UIManager
from ratroyale.backend.tile import Tile
from ratroyale.backend.entity import Entity
from enum import Enum, auto

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ratroyale.input.page_management.page_creator import Page

__all__ = [
    "InteractionType",
    "VisualManagerEvent",
    "RegisterPage_VisualManagerEvent",
    "UnregisterPage_VisualManagerEvent",
    "RegisterVisualComponent_VisualManagerEvent",
    "UnregisterVisualComponent_VisualManagerEvent",
    "TileInteraction_VisualManagerEvent",
    "EntityInteraction_VisualManagerEvent"
]

class InteractionType(Enum):
  HOVER = auto()
  SELECT = auto()

@dataclass
class VisualManagerEvent(EventToken):
  pass

@dataclass
class RegisterPage_VisualManagerEvent(VisualManagerEvent):
  page: Page
  ui_manager: UIManager
  pass

@dataclass
class UnregisterPage_VisualManagerEvent(VisualManagerEvent):
  page: Page

@dataclass
class RegisterVisualComponent_VisualManagerEvent(VisualManagerEvent):
  visual_component: list[VisualComponent]
  interactable: Interactable
  page: Page

@dataclass
class UnregisterVisualComponent_VisualManagerEvent(VisualManagerEvent):
  interactable: Interactable
  page: Page

@dataclass
class TileInteraction_VisualManagerEvent(VisualManagerEvent):
  interaction_type: InteractionType
  tile: Tile

@dataclass
class EntityInteraction_VisualManagerEvent(VisualManagerEvent):
  interaction_type: InteractionType
  entity: Entity