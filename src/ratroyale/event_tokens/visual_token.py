from dataclasses import dataclass
from .base import EventToken

__all__ = [
    "VisualManagerEvent",
    "RegisterPage_VisualManagerEvent",
    "RegisterGameBoardPage_VisualManagerEvent",
    "RegisterGUIVisual_VisualManagerEvent",
    "RegisterTileVisual_VisualManagerEvent",
    "RegisterEntityVisual_VisualManagerEvent"
]

@dataclass
class VisualManagerEvent(EventToken):
  pass

@dataclass
class RegisterPage_VisualManagerEvent(VisualManagerEvent):
  pass

@dataclass
class RegisterGameBoardPage_VisualManagerEvent(VisualManagerEvent):
  pass

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