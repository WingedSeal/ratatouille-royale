from dataclasses import dataclass
from .base import EventToken


@dataclass
class GameManagerEvent[T](EventToken):
    game_action: str
    payload: T | None = None
