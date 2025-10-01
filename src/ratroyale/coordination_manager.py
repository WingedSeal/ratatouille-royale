from typing import Any, TypeVar, cast
from ratroyale.utils import EventQueue
from ratroyale.event_tokens.base import EventToken
from ratroyale.event_tokens.page_token import PageManagerEvent
from ratroyale.event_tokens.game_token import GameManagerEvent
from ratroyale.event_tokens.input_token import InputManagerEvent
from ratroyale.event_tokens.visual_token import VisualManagerEvent


Event_Token_T = TypeVar("Event_Token_T", bound=EventToken)


class MailboxesDict(dict[type[EventToken], EventQueue[Any]]):
    def __getitem__(self, key: type[Event_Token_T]) -> EventQueue[Event_Token_T]:
        return super().__getitem__(key)

    def __setitem__(
        self, key: type[Event_Token_T], value: EventQueue[Event_Token_T]
    ) -> None:
        super().__setitem__(key, value)


class CoordinationManager:
    def __init__(self) -> None:
        self.game_running: bool = True
        self.mailboxes: MailboxesDict = cast(
            MailboxesDict,
            {
                PageManagerEvent: EventQueue[PageManagerEvent](),
                InputManagerEvent: EventQueue[InputManagerEvent](),
                GameManagerEvent: EventQueue[GameManagerEvent](),
                VisualManagerEvent: EventQueue[VisualManagerEvent](),
            },
        )

    def put_message(self, msg: EventToken) -> None:
        for mail_type in self.mailboxes.keys():
            if isinstance(msg, mail_type):
                self.mailboxes[mail_type].put(msg)
                break
        else:
            raise ValueError(f"No mailbox found for message type {type(msg)}")

    def all_mailboxes_empty(self) -> bool:
        return all(q.empty() for q in self.mailboxes.values())

    def stop_game(self) -> None:
        self.game_running = False
