from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.input_token import InputManagerEvent
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *

from ratroyale.frontend.gesture.gesture_data import GestureType

from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.event_binder import input_event_bind
from ratroyale.frontend.pages.page_managers.page_registry import register_page

from ratroyale.frontend.pages.interactables.interactable_builder import InteractableConfig, InteractableType

@register_page
class PauseMenu(Page):
    def __init__(self, coordination_manager: "CoordinationManager"):
        super().__init__(coordination_manager)

        # Config list for all buttons
        configs = [
            InteractableConfig(
                type_key=InteractableType.BUTTON,
                id="resume_button",
                rect=(300, 200, 200, 50),
                text="Continue"
            ),
            InteractableConfig(
                type_key=InteractableType.BUTTON,
                id="quit_button",
                rect=(300, 300, 200, 50),
                text="Quit Game"
            )
        ]

        self.setup_interactables(configs)
        self.setup_input_bindings()
    # region Input Handlers
    @input_event_bind("resume_button", GestureType.CLICK)
    def on_resume_click(self, msg: InputManagerEvent):
        print("Resume clicked!")
        self.coordination_manager.put_message(
            PageNavigationEvent(action_list=[(PageNavigation.POP, None)])
        )

    @input_event_bind("quit_button", GestureType.CLICK)
    def on_quit_click(self, msg: InputManagerEvent):
        print("Quit to menu clicked!")
        self.coordination_manager.put_message(
            PageNavigationEvent(action_list=[
                (PageNavigation.REMOVE_ALL, None),
                (PageNavigation.PUSH, "MainMenu")
            ])
        )
    # endregion