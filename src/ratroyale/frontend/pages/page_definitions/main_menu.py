from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.input_token import InputManagerEvent
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *

from ratroyale.frontend.gesture_management.gesture_data import GestureType

from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.input_binder import bind_to
from ratroyale.frontend.pages.page_managers.page_registry import register_page

from ratroyale.frontend.pages.interactables.interactable_builder import InteractableConfig, InteractableType

@register_page
class MainMenu(Page):
  def __init__(self, coordination_manager: CoordinationManager):
    super().__init__(coordination_manager)

    configs = [
      InteractableConfig(type_key=InteractableType.BUTTON, id="start_button", rect=(100,100,200,50), text="Start"),
      InteractableConfig(type_key=InteractableType.BUTTON, id="quit_button", rect=(100,200,200,50), text="Quit")
    ]

    self.setup_interactables(configs)
    self.setup_bindings()

  # region Input Responses

  @bind_to("start_button", GestureType.CLICK)
  def on_start_click(self, msg: InputManagerEvent):
      print("Start Game clicked!")
      self.coordination_manager.put_message(
          PageNavigationEvent(action_list=[
            (PageNavigation.REMOVE_ALL, None),
            (PageNavigation.PUSH, "PauseButton")])
      )

  @bind_to("quit_button", GestureType.CLICK)
  def on_quit_click(self, msg: InputManagerEvent):
      print("Quit clicked!")
      self.coordination_manager.stop_game()

  # endregion



  