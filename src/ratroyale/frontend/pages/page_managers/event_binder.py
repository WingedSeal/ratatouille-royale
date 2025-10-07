from functools import wraps
from ratroyale.event_tokens.page_token import *

def input_event_bind(element_id: str | None, event_type: int):
  """
  Decorator used for attaching input bindings to methods.
  Multiple bindings can be attached to a single method by stacking these decorators.\n
  Usage example:\n
  @input_event_bind("my_button", GestureType.CLICK)\n
  def handle_click(self, msg: InputManagerEvent):\n
      ...
  """
  def decorator(func):
      bindings = getattr(func, "_input_bindings", [])
      bindings.append((element_id, event_type))
      setattr(func, "_input_bindings", bindings)
      return func  # no wrapper needed
  return decorator

def callback_event_bind(game_action: str):
  """
  Decorator used for attaching input bindings to methods.
  Multiple bindings can be attached to a single method by stacking these decorators.\n
  Usage example:\n
  @bind_to("my_button", GestureType.CLICK)\n
  def handle_click(self, msg: InputManagerEvent):\n
      ...
  """
  def decorator(func):
    @wraps(func)
    def wrapper(self, msg):
      return func(self, msg)

    bindings = getattr(wrapper, "_callback_bindings", [])
    bindings.append(game_action)
    setattr(wrapper, "_callback_bindings", bindings)  
    return wrapper

  return decorator
