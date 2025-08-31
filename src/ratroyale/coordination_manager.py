from ratroyale.utils import EventQueue
from ratroyale.event_tokens import EventToken, InputEvent, PageEvent, GameEvent, VisualEvent

class CoordinationManager:
  def __init__(self):
    self.page_domain_mailbox = EventQueue[PageEvent]()
    self.input_domain_mailbox = EventQueue[InputEvent]()
    self.game_domain_mailbox = EventQueue[GameEvent]()
    self.visual_domain_mailbox = EventQueue[VisualEvent]()

  def put_message(self, msg: EventToken):
    if isinstance(msg, PageEvent):
      self.page_domain_mailbox.put(msg)
    elif isinstance(msg, InputEvent):
      self.input_domain_mailbox.put(msg)
    elif isinstance(msg, GameEvent):
      self.game_domain_mailbox.put(msg)
    elif isinstance(msg, VisualEvent):
      self.visual_domain_mailbox.put(msg)

  def all_mailboxes_empty(self):
    return self.page_domain_mailbox.empty() & self.input_domain_mailbox.empty() & self.game_domain_mailbox.empty() & self.visual_domain_mailbox.empty()