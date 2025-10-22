from dataclasses import dataclass

from .base import EventToken
from .payloads import Payload


@dataclass
class GameManagerEvent(EventToken):
    game_action: str
    payload: Payload | None = None
