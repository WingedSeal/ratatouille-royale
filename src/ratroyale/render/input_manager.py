from ..utils import EventQueue
from .input_event import InputEvent


class InputManager:
    event_queue: EventQueue[InputEvent]
