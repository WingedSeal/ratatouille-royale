from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.input_token import InputManagerEvent
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.game_action import GameAction

from ratroyale.frontend.gesture.gesture_data import GestureType

from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.event_binder import input_event_bind, page_event_bind
from ratroyale.frontend.pages.page_managers.page_registry import register_page

from ratroyale.frontend.pages.interactables.interactable_builder import InteractableConfig, InteractableType

@register_page
class GameBoard(Page):
  def __init__(self, coordination_manager: CoordinationManager) -> None:
    super().__init__(coordination_manager)
    self.setup_interactables([])

  def on_create(self) -> None:
    self.coordination_manager.put_message(GameManagerEvent(
        game_action=GameAction.START_GAME
    ))

  @page_event_bind(GameAction.START_GAME)
  def _start_game(self, msg: PageQueryResponseEvent) -> None:
    if msg.success:
      print("GameBoard received board data:", msg.payload)
    else:
      print("Failed to receive board data:", msg.error_msg)