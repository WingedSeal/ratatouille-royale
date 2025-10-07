from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.input_token import InputManagerEvent
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *

from ratroyale.frontend.gesture.gesture_data import GestureType, to_event

from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.event_binder import input_event_bind
from ratroyale.frontend.pages.page_managers.page_registry import register_page

from ratroyale.frontend.pages.page_elements.element_builder import ElementConfig, UIRegisterForm

import pygame_gui
import pygame

@register_page
class PauseButton(Page):
    def __init__(self, coordination_manager: CoordinationManager):
        super().__init__(coordination_manager, is_blocking=False)

        # --- Instantiate GUI elements directly ---
        gui_elements = [
            UIRegisterForm(
                "pause_button",  # Registration name
                pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(700, 20, 80, 40),
                    text="Pause",
                    manager=self.gui_manager,
                    object_id=pygame_gui.core.ObjectID(
                        class_id="PauseButton",
                        object_id="pause_button"
                    )
                )
            )
        ]

        self.setup_gui_elements(gui_elements)

    # --- Input Responses ---
    @input_event_bind("pause_button", pygame_gui.UI_BUTTON_PRESSED)
    def on_pause_click(self, msg: pygame.event.Event):
        # Strictly typed pygame event
        self.coordination_manager.put_message(
            PageNavigationEvent(action_list=[
                (PageNavigation.OPEN, "PauseMenu")
            ])
        )