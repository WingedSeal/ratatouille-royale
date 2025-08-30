from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

class GUIEventSource(Enum):
  UI_ELEMENT = auto()
  GESTURE = auto()

class PageEventAction(Enum):
  ADD = auto()
  REMOVE = auto()
  REPLACE_TOP = auto()

@dataclass 
class EventToken:
  pass

# Goes to Page Mailbox

@dataclass
class PageEventToken(EventToken):
  page_name: str
  action: PageEventAction
  pass

# Goes to Input Mailbox

@dataclass
class InputEventToken(EventToken):
  source: GUIEventSource
  id: str
  page: str | None = None
  data: Any = None

# Goes to Game Mailbox

@dataclass
class GameDomainToken(EventToken):
  pass

# Goes to Visual Mailbox

@dataclass
class VisualDomainToken(EventToken):
  pass

