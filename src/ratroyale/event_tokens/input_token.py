from dataclasses import dataclass
from ratroyale.input.dispatch_management.action_name import ActionName
from .base import EventToken
from ratroyale.input.interactables_management.interactable import Interactable
from ratroyale.input.gesture_management.gesture_data import GestureData
from ratroyale.input.page_management.page_name import PageName

__all__ = [
   "InputManagerEvent"
]

@dataclass
class InputManagerEvent(EventToken):
  gesture_data: GestureData

  # To be decorated via the input consumption pipeline
  action_key: ActionName 
  interactable: Interactable