from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.input_token import InputManagerEvent
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *

from ratroyale.frontend.gesture.gesture_data import GestureType

from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.event_binder import input_event_bind
from ratroyale.frontend.pages.page_managers.page_registry import register_page

from ratroyale.frontend.pages.page_elements.element_builder import ElementConfig, ElementType

@register_page
class PauseButton(Page):
    def __init__(self, coordination_manager: CoordinationManager):
        super().__init__(coordination_manager, is_blocking=False)

        configs = [
            ElementConfig(
                element_type=ElementType.BUTTON,
                id="pause_button",
                rect=(700, 20, 80, 40),
                text="Pause"
            )
        ]

        self.setup_elements(configs)

    # region Input Responses
    @input_event_bind("pause_button", GestureType.CLICK)
    def on_pause_click(self, msg: InputManagerEvent):
        self.coordination_manager.put_message(
            PageNavigationEvent(action_list=[
                (PageNavigation.OPEN, "PauseMenu")
            ])
        )
    # endregion