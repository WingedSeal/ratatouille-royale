from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.input_token import InputManagerEvent
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *

from ratroyale.input.gesture_management.gesture_data import GestureType

from ..page_managers.base_page import Page
from ratroyale.input.pages.page_managers.input_binder import bind_to
from ratroyale.input.pages.page_managers.page_registry import register_page

from ratroyale.input.pages.interactables.interactable_builder import InteractableConfig, InteractableType

class GameBoard(Page):
  def __init__(self):
    pass