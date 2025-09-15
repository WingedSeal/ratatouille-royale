from dataclasses import dataclass
from .base import EventToken

__all__ = [
  "VisualManagerEvent"
]

@dataclass
class VisualManagerEvent(EventToken):
  pass