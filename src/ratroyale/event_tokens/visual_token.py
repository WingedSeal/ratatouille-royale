from dataclasses import dataclass
from .base import EventToken
from ratroyale.input.page_management.page_creator import Page
from ratroyale.visual.asset_management.visual_component import VisualComponent
from ratroyale.input.page_management.interactable import Interactable

__all__ = [
    "VisualManagerEvent",
    "RegisterPage_VisualManagerEvent",
    "UnregisterPage_VisualManagerEvent",
    "RegisterVisualComponent_VisualManagerEvent",
    "UnregisterVisualComponent_VisualManagerEvent"
]

@dataclass
class VisualManagerEvent(EventToken):
  pass

@dataclass
class RegisterPage_VisualManagerEvent(VisualManagerEvent):
  page: Page
  pass

@dataclass
class UnregisterPage_VisualManagerEvent(VisualManagerEvent):
  page: Page

@dataclass
class RegisterVisualComponent_VisualManagerEvent(VisualManagerEvent):
  visual_component: VisualComponent
  interactable: Interactable
  page: Page

@dataclass
class UnregisterVisualComponent_VisualManagerEvent(VisualManagerEvent):
  interactable: Interactable
  page: Page