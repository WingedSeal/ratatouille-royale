from ratroyale.event_tokens.page_token import *
from typing import Callable, TypeVar, ParamSpec

P = ParamSpec("P")  # Parameter specification
R = TypeVar("R")  # Return type


def input_event_bind(
    element_id: str | None, event_type: int
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator used for attaching input bindings to methods.
    Multiple bindings can be attached to a single method by stacking these decorators.\n
    Usage example:\n
    @input_event_bind("my_button", GestureType.CLICK)\n
    def handle_click(self, msg: InputManagerEvent):\n
        ...
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        bindings = getattr(func, "_input_bindings", [])
        bindings.append((element_id, event_type))
        setattr(func, "_input_bindings", bindings)
        return func  # no wrapper needed

    return decorator


def callback_event_bind(
    callback_action: str,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator used for attaching input bindings to methods.
    Multiple bindings can be attached to a single method by stacking these decorators.\n
    Usage example:\n
    @bind_to("my_button", GestureType.CLICK)\n
    def handle_click(self, msg: InputManagerEvent):\n
        ...
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:

        bindings = getattr(func, "_callback_bindings", [])
        bindings.append(callback_action)
        setattr(func, "_callback_bindings", bindings)
        return func

    return decorator
