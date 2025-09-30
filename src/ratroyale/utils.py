from queue import Queue, Empty
from typing import TypeVar

T = TypeVar("T")


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


class EventQueue(Queue[T]):
    def get_or_none(self) -> T | None:
        try:
            return self.get_nowait()
        except Empty:
            return None
