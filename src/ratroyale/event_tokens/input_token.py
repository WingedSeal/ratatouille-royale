import pygame

from dataclasses import dataclass
from .base import EventToken
from ratroyale.frontend.gesture.gesture_data import GestureData, GESTURE_EVENT_MAP
from typing import TypeVar, Generic

__all__ = [
   "InputManagerEvent"
]

T = TypeVar("T")

@dataclass
class InputManagerEvent(Generic[T], EventToken):
   element_id: str
   gesture_data: GestureData
   payload: T | None = None

def post_gesture_event(input_manager_event: InputManagerEvent):
   """
    Posts a GestureData event to Pygame's event queue using the
    hybrid gesture-specific event type mapping. The listener can
    access both gesture_data and element_id from the event.
    """
   event_type: int = GESTURE_EVENT_MAP[input_manager_event.gesture_data.gesture_type]
   pygame.event.post(
      pygame.event.Event(
         event_type, 
         input_manager_event=input_manager_event
         )
      )