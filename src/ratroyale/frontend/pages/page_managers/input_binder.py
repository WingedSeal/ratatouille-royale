from functools import wraps
from ratroyale.frontend.gesture_management.gesture_data import GestureType

def bind_to(widget_id: str, gesture_type: GestureType):
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

    bindings = getattr(wrapper, "_bindings", [])
    bindings.append((widget_id, gesture_type))
    setattr(wrapper, "_bindings", bindings)  
    return wrapper

  return decorator
