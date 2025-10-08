from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.input_token import InputManagerEvent
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *

from ratroyale.frontend.gesture.gesture_data import GestureType, to_event

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
class MainMenu(Page):
    def __init__(self, coordination_manager: CoordinationManager) -> None:
        super().__init__(coordination_manager, theme_name="main_menu")

        gui_elements = [
            UIRegisterForm(
                "start_button",  # <- registration name. This is what will be used for removal / management.
                pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(100, 100, 200, 50),
                    text="Start",
                    manager=self.gui_manager,
                    object_id=pygame_gui.core.ObjectID(
                        class_id="MainMenuButton", object_id="start_button"
                    ),
                    # object_id is returned when a pygame event processed by pygame_gui fires.
                    # use object_id to listen to inputs, not registration name,
                    # though it is advisable (but not enforced) to make them the same.
                ),
            ),
            UIRegisterForm(
                "quit_button",
                pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(100, 200, 200, 50),
                    text="Quit",
                    manager=self.gui_manager,
                    object_id=pygame_gui.core.ObjectID(
                        class_id="MainMenuButton", object_id="quit_button"
                    ),
                ),
            ),
            UIRegisterForm(
                "gui_demo_button",
                pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(100, 300, 200, 50),
                    text="Go to GUI demo",
                    manager=self.gui_manager,
                    object_id=pygame_gui.core.ObjectID(
                        class_id="MainMenuButton", object_id="gui_demo_button"
                    ),
                ),
            ),
            UIRegisterForm(
                "element_demo_button",
                pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(400, 300, 200, 50),
                    text="Go to Element demo",
                    manager=self.gui_manager,
                    object_id=pygame_gui.core.ObjectID(
                        class_id="MainMenuButton", object_id="element_demo_button"
                    ),
                ),
            ),
        ]

        self.setup_gui_elements(gui_elements)

    # region Input Responses

    @input_event_bind("start_button", pygame_gui.UI_BUTTON_PRESSED)
    def on_start_click(self, msg: pygame.event.Event) -> None:
        self.coordination_manager.put_message(
            PageNavigationEvent(
                action_list=[
                    (PageNavigation.CLOSE_ALL, None),
                    (PageNavigation.OPEN, "GameBoard"),
                    (PageNavigation.OPEN, "PauseButton"),
                    (PageNavigation.OPEN, "EntityList"),
                ]
            )
        )

    @input_event_bind("quit_button", pygame_gui.UI_BUTTON_PRESSED)
    def _on_quit_click(self, msg: pygame.event.Event) -> None:
        self.coordination_manager.stop_game()

    @input_event_bind("gui_demo_button", pygame_gui.UI_BUTTON_PRESSED)
    def _on_gui_demo_click(self, msg: pygame.event.Event) -> None:
        self.post(
            PageNavigationEvent(
                action_list=[
                    (PageNavigation.CLOSE_ALL, None),
                    (PageNavigation.OPEN, "GUIDemo"),
                ]
            )
        )

    @input_event_bind("element_demo_button", pygame_gui.UI_BUTTON_PRESSED)
    def _on_element_demo_click(self, msg: pygame.event.Event) -> None:
        print("Element demo button clicked")

    # endregion
