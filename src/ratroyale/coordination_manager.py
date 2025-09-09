from ratroyale.utils import EventQueue
from ratroyale.event_tokens import EventToken, InputManagerEvent, PageManagerEvent, GameManagerEvent, VisualEvent

class CoordinationManager:
  def __init__(self):
    self.page_domain_mailbox = EventQueue[PageManagerEvent]()
    self.input_domain_mailbox = EventQueue[InputManagerEvent]()
    self.game_domain_mailbox = EventQueue[GameManagerEvent]()
    self.visual_domain_mailbox = EventQueue[VisualEvent]()

  def put_message(self, msg: EventToken):
    if isinstance(msg, PageManagerEvent):
      self.page_domain_mailbox.put(msg)
    elif isinstance(msg, InputManagerEvent):
      self.input_domain_mailbox.put(msg)
    elif isinstance(msg, GameManagerEvent):
      self.game_domain_mailbox.put(msg)
    elif isinstance(msg, VisualEvent):
      self.visual_domain_mailbox.put(msg)

  def all_mailboxes_empty(self):
    return self.page_domain_mailbox.empty() & self.input_domain_mailbox.empty() & self.game_domain_mailbox.empty() & self.visual_domain_mailbox.empty()