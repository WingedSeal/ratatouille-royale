from typing import Type

from ratroyale.utils import EventQueue
from ratroyale.event_tokens.base import EventToken
from ratroyale.event_tokens.page_token import PageManagerEvent
from ratroyale.event_tokens.game_token import GameManagerEvent
from ratroyale.event_tokens.input_token import InputManagerEvent
from ratroyale.event_tokens.visual_token import VisualManagerEvent


class CoordinationManager:
    def __init__(self):
        self.game_running = True
    
        self.mailboxes: dict[Type[EventToken], EventQueue] = {
            PageManagerEvent: EventQueue[PageManagerEvent](),
            InputManagerEvent: EventQueue[InputManagerEvent](),
            GameManagerEvent: EventQueue[GameManagerEvent](),
            VisualManagerEvent: EventQueue[VisualManagerEvent](),
        }

    def put_message(self, msg: EventToken):
        for mail_type in self.mailboxes.keys():
            if isinstance(msg, mail_type):
                self.mailboxes[mail_type].put(msg)
                break
        else:
            raise ValueError(f"No mailbox found for message type {type(msg)}")

    def all_mailboxes_empty(self) -> bool:
        return all(q.empty() for q in self.mailboxes.values())
    
    def stop_game(self):
        self.game_running = False
