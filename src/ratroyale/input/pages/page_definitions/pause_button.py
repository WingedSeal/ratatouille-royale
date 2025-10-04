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

@register_page
class PauseButton(Page):
    def __init__(self, coordination_manager: CoordinationManager):
        super().__init__(coordination_manager)

        configs = [
            InteractableConfig(
                type_key=InteractableType.BUTTON,
                id="pause_button",
                rect=(700, 20, 80, 40),
                text="Pause"
            )
        ]

        self.setup_interactables(configs)
        self.setup_bindings()

    # region Input Responses
    @bind_to("pause_button", GestureType.CLICK)
    def on_pause_click(self, msg: InputManagerEvent):
        print("Pause clicked!")
        self.coordination_manager.put_message(
            PageNavigationEvent(action_list=[
                (PageNavigation.PUSH, "PauseMenu")
            ])
        )
    # endregion