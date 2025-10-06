from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.input_token import InputManagerEvent
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *

from ratroyale.frontend.gesture.gesture_data import GestureType, to_event

from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.event_binder import input_event_bind
from ratroyale.frontend.pages.page_managers.page_registry import register_page

from ratroyale.frontend.pages.page_elements.element_builder import ElementConfig, ElementType, GUITheme

@register_page
class MainMenu(Page):
  def __init__(self, coordination_manager: CoordinationManager):
    super().__init__(coordination_manager, theme_name="main_menu")

    configs = [
      ElementConfig(
          element_type=ElementType.BUTTON, 
          id="start_button", 
          rect=(100,100,200,50), 
          text="Start",
          gui_theme=GUITheme(class_id="MainMenuButton", object_id="start_button")
          ),
      ElementConfig(
          element_type=ElementType.BUTTON, 
          id="quit_button", 
          rect=(100,200,200,50), 
          text="Quit",
          gui_theme=GUITheme(class_id="smth", object_id="start_button")
          )
    ]

    self.setup_elements(configs)

  # region Input Responses

  @input_event_bind("start_button", to_event(GestureType.CLICK))
  def on_start_click(self, msg: InputManagerEvent):
      self.coordination_manager.put_message(
        PageNavigationEvent(action_list=[
          (PageNavigation.CLOSE_ALL, None),
          (PageNavigation.OPEN, "GameBoard"),
          (PageNavigation.OPEN, "PauseButton")])
      )

  @input_event_bind("quit_button", to_event(GestureType.CLICK))
  def on_quit_click(self, msg: InputManagerEvent):
      self.coordination_manager.stop_game()

  @input_event_bind("child_button", to_event(GestureType.CLICK))
  def test(self, msg: InputManagerEvent):
      print("Test function called")

  # endregion



  