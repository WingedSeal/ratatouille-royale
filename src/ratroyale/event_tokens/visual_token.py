from dataclasses import dataclass
from .base import EventToken
from ratroyale.input.page_management.page_creator import Page

__all__ = [
    "VisualManagerEvent",
    "RegisterPage_VisualManagerEvent",
    "UnregisterPage_VisualManagerEvent",
    "RegisterGUIVisual_VisualManagerEvent",
    "RegisterTileVisual_VisualManagerEvent",
    "RegisterEntityVisual_VisualManagerEvent",
    "UnregisterGUIVisual_VisualManagerEvent",
    "UnregisterTileVisual_VisualManagerEvent",
    "UnregisterEntityVisual_VisualManagerEvent"
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
class RegisterGUIVisual_VisualManagerEvent(VisualManagerEvent):
  # TODO: add GUI visual data
  pass

@dataclass
class RegisterTileVisual_VisualManagerEvent(VisualManagerEvent):
  # TODO: add tile data
  pass

@dataclass
class RegisterEntityVisual_VisualManagerEvent(VisualManagerEvent):
  # TODO: add entity data
  pass

@dataclass
class UnregisterGUIVisual_VisualManagerEvent(VisualManagerEvent):
  # TODO: add GUI visual data
  pass

@dataclass
class UnregisterTileVisual_VisualManagerEvent(VisualManagerEvent):
  # TODO: add tile data
  pass

@dataclass
class UnregisterEntityVisual_VisualManagerEvent(VisualManagerEvent):
  # TODO: add entity data
  pass