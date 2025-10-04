from functools import wraps
from ratroyale.frontend.gesture.gesture_data import GestureType
from ratroyale.event_tokens.page_token import *

def input_event_bind(widget_id: str, gesture_type: GestureType):
  """
  Decorator used for attaching input bindings to methods.
  Multiple bindings can be attached to a single method by stacking these decorators.\n
  Usage example:\n
  @input_event_bind("my_button", GestureType.CLICK)\n
  def handle_click(self, msg: InputManagerEvent):\n
      ...
  """
  def decorator(func):
    @wraps(func)
    def wrapper(self, msg):
      return func(self, msg)

    bindings = getattr(wrapper, "input_bindings", [])
    bindings.append((widget_id, gesture_type))
    setattr(wrapper, "input_bindings", bindings)  
    return wrapper

  return decorator

def page_event_bind(action_name: str):
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

    bindings = getattr(wrapper, "page_bindings", [])
    bindings.append(action_name)
    setattr(wrapper, "page_bindings", bindings)  
    return wrapper

  return decorator
