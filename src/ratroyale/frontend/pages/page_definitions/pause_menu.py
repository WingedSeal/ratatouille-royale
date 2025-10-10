from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.input_token import InputManagerEvent
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *

from ratroyale.frontend.gesture.gesture_data import GestureType

from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.event_binder import input_event_bind
from ratroyale.frontend.pages.page_managers.page_registry import register_page

from ratroyale.frontend.pages.page_elements.element_builder import (
    ElementConfig,
    UIRegisterForm,
)

import pygame_gui
import pygame


@register_page
class PauseMenu(Page):
    def __init__(self, coordination_manager: "CoordinationManager") -> None:
        super().__init__(
            coordination_manager, base_color=(0, 0, 0, 128), theme_name="pause_menu"
        )

    def define_initial_gui(self) -> list[UIRegisterForm]:
        return [
            UIRegisterForm(
                "resume_button",
                pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(300, 200, 200, 50),
                    text="Continue",
                    manager=self.gui_manager,
                    object_id=pygame_gui.core.ObjectID(
                        class_id="PauseMenuButton", object_id="resume_button"
                    ),
                ),
            ),
            UIRegisterForm(
                "quit_button",
                pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(300, 300, 200, 50),
                    text="Quit Game",
                    manager=self.gui_manager,
                    object_id=pygame_gui.core.ObjectID(
                        class_id="PauseMenuButton", object_id="quit_button"
                    ),
                ),
            ),
        ]

    # --- Input Handlers ---
    @input_event_bind("resume_button", pygame_gui.UI_BUTTON_PRESSED)
    def on_resume_click(self, msg: pygame.event.Event) -> None:
        self.post(PageNavigationEvent(action_list=[(PageNavigation.CLOSE_TOP, None)]))

    @input_event_bind("quit_button", pygame_gui.UI_BUTTON_PRESSED)
    def on_quit_click(self, msg: pygame.event.Event) -> None:
        self.post(
            PageNavigationEvent(
                action_list=[
                    (PageNavigation.CLOSE_ALL, None),
                    (PageNavigation.OPEN, "MainMenu"),
                ]
            )
        )
