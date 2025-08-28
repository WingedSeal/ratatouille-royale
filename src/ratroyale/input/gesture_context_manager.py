class GestureContextManager:
  def __init__(self, gesture_interpreter):
    self.gesture_interpreter = gesture_interpreter

  def __enter__(self):
    # Initialize or prepare gesture_interpreter if needed
    return self.gesture_interpreter

  def __exit__(self, exc_type, exc_val, exc_tb):
    # Clean up resources if needed
    pass