from ratroyale.utils import EventQueue
from ratroyale.event_tokens import EventToken, InputEventToken, PageEventToken, GameDomainToken, VisualDomainToken

class CoordinationManager:
  def __init__(self):
    self.page_domain_mailbox = EventQueue[PageEventToken]()
    self.input_domain_mailbox = EventQueue[InputEventToken]()
    self.game_domain_mailbox = EventQueue[GameDomainToken]()
    self.visual_domain_mailbox = EventQueue[VisualDomainToken]()

  def put_message(self, msg: EventToken):
    if isinstance(msg, PageEventToken):
      self.page_domain_mailbox.put(msg)
    elif isinstance(msg, InputEventToken):
      self.input_domain_mailbox.put(msg)
    elif isinstance(msg, GameDomainToken):
      self.game_domain_mailbox.put(msg)
    elif isinstance(msg, VisualDomainToken):
      self.visual_domain_mailbox.put(msg)

  def all_mailboxes_empty(self):
    return self.page_domain_mailbox.empty() & self.input_domain_mailbox.empty() & self.game_domain_mailbox.empty() & self.visual_domain_mailbox.empty()