from typing import Any, TypeVar, cast

from ratroyale.event_tokens.base import EventToken
from ratroyale.event_tokens.game_token import GameManagerEvent
from ratroyale.event_tokens.page_token import PageManagerEvent
from ratroyale.event_tokens.visual_token import VisualManagerEvent
from ratroyale.utils import EventQueue

Event_Token_T = TypeVar("Event_Token_T", bound=EventToken)


class MailboxesDict(dict[type[EventToken], EventQueue[Any]]):
    def __getitem__(self, key: type[Event_Token_T]) -> EventQueue[Event_Token_T]:
        return super().__getitem__(key)

    def __setitem__(
        self, key: type[Event_Token_T], value: EventQueue[Event_Token_T]
    ) -> None:
        super().__setitem__(key, value)


class CoordinationManager:
    mailboxes: MailboxesDict = cast(
        MailboxesDict,
        {
            PageManagerEvent: EventQueue[PageManagerEvent](),
            GameManagerEvent: EventQueue[GameManagerEvent](),
            VisualManagerEvent: EventQueue[VisualManagerEvent](),
        },
    )
    game_running: bool = True

    @classmethod
    def put_message(cls, msg: EventToken) -> None:
        for mail_type in cls.mailboxes.keys():
            if isinstance(msg, mail_type):
                cls.mailboxes[mail_type].put(msg)
                break
        else:
            raise ValueError(f"No mailbox found for message type {type(msg)}")

    def all_mailboxes_empty(self) -> bool:
        return all(q.empty() for q in self.mailboxes.values())

    def stop_game(self) -> None:
        self.game_running = False
