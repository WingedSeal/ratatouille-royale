from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.input_token import InputManagerEvent
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *

from ratroyale.frontend.gesture.gesture_data import GestureType, to_event

from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.event_binder import input_event_bind
from ratroyale.frontend.pages.page_managers.page_registry import register_page

from ratroyale.frontend.pages.page_elements.element_builder import ElementConfig

@register_page
class PauseMenu(Page):
    def __init__(self, coordination_manager: "CoordinationManager"):
        super().__init__(coordination_manager, base_color=(0,0,0,128))

        configs = [
            ElementConfig(
                element_type=ElementType.BUTTON,
                id="resume_button",
                rect=(300, 200, 200, 50),
                text="Continue"
            ),
            ElementConfig(
                element_type=ElementType.BUTTON,
                id="quit_button",
                rect=(300, 300, 200, 50),
                text="Quit Game"
            )
        ]

        self.setup_elements(configs)

    # region Input Handlers
    @input_event_bind("resume_button", to_event(GestureType.CLICK))
    def on_resume_click(self, msg: InputManagerEvent):
        print("Resume clicked!")
        self.coordination_manager.put_message(
            PageNavigationEvent(action_list=[(PageNavigation.CLOSE_TOP, None)])
        )

    @input_event_bind("quit_button", to_event(GestureType.CLICK))
    def on_quit_click(self, msg: InputManagerEvent):
        print("Quit to menu clicked!")
        self.coordination_manager.put_message(
            PageNavigationEvent(action_list=[
                (PageNavigation.CLOSE_ALL, None),
                (PageNavigation.OPEN, "MainMenu")
            ])
        )
    # endregion