from queue import Empty, Queue
from typing import TypeVar, cast

T = TypeVar("T")


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


class EventQueue(Queue[T]):
    def get_or_none(self) -> T | None:
        try:
            return self.get_nowait()
        except Empty:
            return None

    def peek(self) -> T | None:
        with self.mutex:
            if len(self.queue) == 0:
                return None
            return cast(T, self.queue[0])
