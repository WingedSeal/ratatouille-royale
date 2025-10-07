import pygame

from dataclasses import dataclass
from .base import EventToken
from ratroyale.frontend.gesture.gesture_data import GestureData, GESTURE_EVENT_MAP
from typing import TypeVar, Generic

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
   
def get_id(event: pygame.event.Event) -> str | None:
    """
    Extracts the element_id or ui_object_id from a pygame or pygame_gui event.

    - pygame_gui events: return ui_object_id
    - custom gesture events: return element_id from input_manager_event
    - others: return None
    """
    event_type = event.type

    # --- Case 1: pygame_gui events ---
    if hasattr(event, "ui_object_id"):
        return getattr(event, "ui_object_id")

    # --- Case 2: our gesture events ---
    if event_type in GESTURE_EVENT_MAP.values():
         input_manager_event = getattr(event, "input_manager_event", None)
         if isinstance(input_manager_event, InputManagerEvent):
            return input_manager_event.element_id

    # --- Case 3: unrelated event ---
    return None

def get_gesture_data(event: pygame.event.Event) -> GestureData | None:
    """Extract GestureData from an event or its input_manager_event wrapper."""
    gesture_data = getattr(event, "gesture_data", None)

    # Check top level first
    if isinstance(gesture_data, GestureData):
        return gesture_data

    # If not found, check nested input_manager_event
    inner = getattr(event, "input_manager_event", None)
    if inner and hasattr(inner, "gesture_data") and isinstance(inner.gesture_data, GestureData):
        return inner.gesture_data

    raise TypeError(f"Event {event} does not contain GestureData.")

def get_payload(event: pygame.event.Event) -> object:
    """Extracts the payload from an InputManagerEvent if present, else returns None."""
    input_mgr_event = getattr(event, "input_manager_event", None)
    if isinstance(input_mgr_event, InputManagerEvent):
        return input_mgr_event.payload
    return None