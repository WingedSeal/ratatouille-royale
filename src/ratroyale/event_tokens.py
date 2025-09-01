from dataclasses import dataclass
from typing import Any
from ratroyale.input.page.page_config import PageName
from ratroyale.input.constants import PageEventAction, GUIEventSource, ActionKey

@dataclass 
class EventToken:
  pass

# Goes to Page Mailbox

@dataclass
class PageEvent(EventToken):
  page_name: PageName
  action: PageEventAction
  pass

# Goes to Input Mailbox

@dataclass
class InputEvent(EventToken):
  source: GUIEventSource
  action_key: ActionKey
  page_name: PageName
  data: Any = None

# Goes to Game Mailbox

@dataclass
class GameEvent(EventToken):
  pass

# example class
class CardPlacementGameEvent(GameEvent):
  pass

# Goes to Visual Mailbox

@dataclass
class VisualEvent(EventToken):
  pass

