import dis
from queue import Empty, Queue
from typing import Any, Callable, TypeVar, cast

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


def is_ellipsis_body(func: Callable[..., Any]) -> bool:
    """Checks if a function's body is solely the ellipsis (...)"""
    instructions = list(dis.get_instructions(func))

    if len(instructions) != 4:
        return False
    return (
        instructions[0].opname == "LOAD_CONST"
        and instructions[0].argval is Ellipsis
        and instructions[1].opname == "POP_TOP"
        and instructions[2].opname == "LOAD_CONST"
        and instructions[2].argval is None
        and instructions[3].opname == "RETURN_VALUE"
    )
