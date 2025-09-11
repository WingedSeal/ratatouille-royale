from ratroyale.utils import EventQueue
from ratroyale.event_tokens.base import EventToken
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.input_token import *
from ratroyale.event_tokens.visual_token import *


class CoordinationManager:
  def __init__(self):
    self.page_domain_mailbox = EventQueue[PageManagerEvent]()
    self.input_domain_mailbox = EventQueue[InputManagerEvent]()
    self.game_domain_mailbox = EventQueue[GameManagerEvent]()
    self.visual_domain_mailbox = EventQueue[VisualManagerEvent]()

  def put_message(self, msg: EventToken):
    if isinstance(msg, PageManagerEvent):
      self.page_domain_mailbox.put(msg)
    elif isinstance(msg, InputManagerEvent):
      self.input_domain_mailbox.put(msg)
    elif isinstance(msg, GameManagerEvent):
      self.game_domain_mailbox.put(msg)
    elif isinstance(msg, VisualManagerEvent):
      self.visual_domain_mailbox.put(msg)

  def all_mailboxes_empty(self):
    return self.page_domain_mailbox.empty() & self.input_domain_mailbox.empty() & self.game_domain_mailbox.empty() & self.visual_domain_mailbox.empty()