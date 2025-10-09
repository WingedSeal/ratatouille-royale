from dataclasses import dataclass

from .base import EventToken

__all__ = [
    "GameManagerEvent",
    "RequestStart_GameManagerEvent",
    "CardPlacement_GameManagerEvent",
]


@dataclass
class GameManagerEvent(EventToken):
    pass


@dataclass
class RequestStart_GameManagerEvent(GameManagerEvent):
    map_path: str | None = (
        None  # Could change to enums that represents different premade stages later.
    )
    pass


@dataclass
class CardPlacement_GameManagerEvent(GameManagerEvent):
    pass
