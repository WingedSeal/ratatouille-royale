from dataclasses import dataclass
from ratroyale.input.page.page_config import PageName
from ratroyale.input.constants import ActionKey, GestureKey
import pygame
from ratroyale.backend.board import Board

@dataclass 
class EventToken:
  pass

# Goes to Page Mailbox

@dataclass
class PageEvent(EventToken):
  pass

@dataclass
class AddPageEvent(PageEvent):
    page_name: PageName

@dataclass
class RemovePageEvent(PageEvent):
    page_name: PageName | None = None

@dataclass
class ReplaceTopPageEvent(PageEvent):
    page_name: PageName

@dataclass
class ConfirmStartGamePageEvent(PageEvent):
   board: Board | None

# Goes to Input Mailbox

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
    raw_event: pygame.event.Event | None = None # Optional

@dataclass
class InputEvent(EventToken):
  gesture_data: GestureData

  # To be decorated via the input consumption pipeline
  action_key: ActionKey 
  page_name: PageName

# Goes to Game Mailbox

@dataclass
class GameEvent(EventToken):
  pass

# example class
class RequestStartGameEvent(GameEvent):
  map_path: str | None = None # Could change to enums that represents different premade stages later.
  pass

class CardPlacementGameEvent(GameEvent):
  pass

# Goes to Visual Mailbox

@dataclass
class VisualEvent(EventToken):
  pass

