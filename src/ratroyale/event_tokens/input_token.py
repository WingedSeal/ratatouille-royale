from dataclasses import dataclass
from .base import EventToken
from ratroyale.input.gesture_management.gesture_data import GestureData
from typing import TypeVar, Generic

__all__ = [
   "InputManagerEvent"
]

T = TypeVar('T')

@dataclass
class InputManagerEvent(Generic[T], EventToken):
    interactable_id: str
    gesture_data: GestureData
    payload: T | None = None