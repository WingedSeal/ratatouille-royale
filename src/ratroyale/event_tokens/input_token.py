from dataclasses import dataclass

import pygame

from ratroyale.input.constants import ActionKey, GestureKey, PageName

from .base import EventToken

__all__ = ["GestureData", "InputManagerEvent"]


@dataclass
class GestureData:
    gesture_key: GestureKey

    start_pos: tuple[int, int] | None = None
    end_pos: tuple[int, int] | None = None
    current_pos: tuple[int, int] | None = None
    delta: tuple[int, int] | None = None
    duration: float | None = None
    velocity: tuple[float, float] | None = None
    key: str | None = None
    mouse: str | None = None
    scroll_amount: int | None = None
    raw_event: pygame.event.Event | None = None


@dataclass
class InputManagerEvent(EventToken):
    gesture_data: GestureData

    # To be decorated via the input consumption pipeline
    action_key: ActionKey
    page_name: PageName
