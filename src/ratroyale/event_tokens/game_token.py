from dataclasses import dataclass
from .base import EventToken
from typing import TypeVar, Generic

T = TypeVar("T")


@dataclass
class GameManagerEvent(Generic[T], EventToken):
    game_action: str
    payload: T | None = None
