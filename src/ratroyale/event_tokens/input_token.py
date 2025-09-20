from dataclasses import dataclass
from ratroyale.input.page.page_config import PageName
from ratroyale.input.constants import ActionKey, GestureKey
import pygame
from .base import EventToken
from ratroyale.input.page.interactable import Interactable

__all__ = [
   "GestureData",
   "InputManagerEvent"
   ]

@dataclass
class GestureData:
    gesture_key: GestureKey

    start_pos: tuple[int, int] | None = None
    end_pos: tuple[int, int] | None = None
    current_pos: tuple[int, int] | None = None
    delta: tuple[int, int] | None = None
    duration: float | None = None
    velocity: tuple[float, float] | None = None
    key: str | None = None
    mouse: str | None = None
    scroll_amount: int | None = None
    raw_event: pygame.event.Event | None = None

@dataclass
class InputManagerEvent(EventToken):
  gesture_data: GestureData

  # To be decorated via the input consumption pipeline
  action_key: ActionKey 
  interactable: Interactable