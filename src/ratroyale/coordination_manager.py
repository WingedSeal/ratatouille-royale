from typing import TypeVar, Type, Dict

from ratroyale.utils import EventQueue
from ratroyale.event_tokens.base import EventToken
from ratroyale.event_tokens.page_token import PageManagerEvent
from ratroyale.event_tokens.game_token import GameManagerEvent
from ratroyale.event_tokens.input_token import InputManagerEvent
from ratroyale.event_tokens.visual_token import VisualManagerEvent


T = TypeVar("T", bound=EventToken)

class CoordinationManager:
    def __init__(self):
        # Map each EventToken type to its mailbox queue
        self.mailboxes: Dict[Type[EventToken], EventQueue] = {
            PageManagerEvent: EventQueue[PageManagerEvent](),
            InputManagerEvent: EventQueue[InputManagerEvent](),
            GameManagerEvent: EventQueue[GameManagerEvent](),
            VisualManagerEvent: EventQueue[VisualManagerEvent](),
        }

    def put_message(self, msg: EventToken):
      if isinstance(msg, PageManagerEvent):
          self.mailboxes[PageManagerEvent].put(msg)
      elif isinstance(msg, InputManagerEvent):
          self.mailboxes[InputManagerEvent].put(msg)
      elif isinstance(msg, GameManagerEvent):
          self.mailboxes[GameManagerEvent].put(msg)
      elif isinstance(msg, VisualManagerEvent):
          self.mailboxes[VisualManagerEvent].put(msg)
      else:
          raise ValueError(f"No mailbox found for message type {type(msg)}")

    def all_mailboxes_empty(self) -> bool:
        return all(q.empty() for q in self.mailboxes.values())
