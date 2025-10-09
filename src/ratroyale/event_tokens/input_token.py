import pygame

from dataclasses import dataclass
from .base import EventToken
from ratroyale.frontend.gesture.gesture_data import GestureData, GestureType
from typing import Any


@dataclass
class InputManagerEvent[T](EventToken):
    element_id: str | None
    gesture_data: GestureData
    payload: T | None = None


def post_gesture_event(input_manager_event: InputManagerEvent[Any]) -> None:
    """
    Posts a GestureData event to Pygame's event queue using the
    hybrid gesture-specific event type mapping. The listener can
    access both gesture_data and element_id from the event.
    """
    event_type: int = input_manager_event.gesture_data.gesture_type.value
    pygame.event.post(
        pygame.event.Event(event_type, input_manager_event=input_manager_event)
    )


def get_id(event: pygame.event.Event) -> str | None:
    """
    Extracts the element_id or ui_object_id from a pygame or pygame_gui event.

    - pygame_gui events: return ui_object_id
    - custom gesture events: return element_id from input_manager_event
    - others: return None
    """
    event_type = event.type

    is_pygame_gui_event = hasattr(event, "ui_object_id")
    if is_pygame_gui_event:
        value = getattr(event, "ui_object_id")
        if isinstance(value, str):
            return value
        raise TypeError("pygame_gui event has invalid ui_object_id")

    is_custom_gesture_event = event_type in [g.value for g in GestureType]
    if is_custom_gesture_event:
        input_manager_event = getattr(event, "input_manager_event", None)
        if isinstance(input_manager_event, InputManagerEvent):
            return input_manager_event.element_id
        raise TypeError("Gesture event missing InputManagerEvent or has wrong type")

    return None


def get_gesture_data(event: pygame.event.Event) -> GestureData:
    """Extract GestureData from an event or its input_manager_event wrapper."""
    gesture_data = getattr(event, "gesture_data", None)

    # Check top level first
    if isinstance(gesture_data, GestureData):
        return gesture_data

    # If not found, check nested input_manager_event
    inner = getattr(event, "input_manager_event", None)
    if (
        inner
        and hasattr(inner, "gesture_data")
        and isinstance(inner.gesture_data, GestureData)
    ):
        return inner.gesture_data

    raise TypeError(f"Event {event} does not contain GestureData.")


def get_payload(event: pygame.event.Event) -> object:
    """Extracts the payload from an InputManagerEvent if present, else returns None."""
    input_mgr_event = getattr(event, "input_manager_event", None)
    if isinstance(input_mgr_event, InputManagerEvent):
        return input_mgr_event.payload
    return None
