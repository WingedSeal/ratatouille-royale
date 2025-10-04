from dataclasses import dataclass
from .base import EventToken
from ratroyale.frontend.visual.asset_management.visual_component import VisualComponent
from ratroyale.frontend.pages.interactables.interactable import Interactable
from pygame_gui.ui_manager import UIManager
from ratroyale.backend.tile import Tile
from ratroyale.backend.entity import Entity


__all__ = [
    "VisualManagerEvent",
    "RegisterPage_VisualManagerEvent",
    "UnregisterPage_VisualManagerEvent",
    "RegisterVisualComponent_VisualManagerEvent",
    "UnregisterVisualComponent_VisualManagerEvent",
    "EntityMovementConfirmation_VisualManagerEvent"
]

@dataclass
class VisualManagerEvent(EventToken):
  pass

@dataclass
class RegisterPage_VisualManagerEvent(VisualManagerEvent):
  ui_manager: UIManager

@dataclass
class UnregisterPage_VisualManagerEvent(VisualManagerEvent):
  pass

@dataclass
class RegisterVisualComponent_VisualManagerEvent(VisualManagerEvent):
  visual_component: list[VisualComponent]
  interactable: Interactable

@dataclass
class UnregisterVisualComponent_VisualManagerEvent(VisualManagerEvent):
  interactable: Interactable

# @dataclass
# class TileInteraction_VisualManagerEvent(VisualManagerEvent):
#   interaction_type: InteractionType
#   tile: Tile

# @dataclass
# class EntityInteraction_VisualManagerEvent(VisualManagerEvent):
#   interaction_type: InteractionType
#   entity: Entity

@dataclass
class EntityMovementConfirmation_VisualManagerEvent(VisualManagerEvent):
  success: bool
  error_msg: str | None

  new_coord: tuple[float, float] | None
