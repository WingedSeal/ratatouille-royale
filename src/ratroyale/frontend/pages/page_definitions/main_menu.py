import pygame
import pygame_gui

from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.visual_token import *
from ratroyale.frontend.pages.page_managers.event_binder import input_event_bind
from ratroyale.frontend.pages.page_managers.page_registry import register_page

from ratroyale.frontend.pages.page_elements.element import (
    ElementWrapper,
    ui_element_wrapper,
)
from ratroyale.frontend.pages.page_elements.spatial_component import (
    Camera,
)


from ..page_managers.base_page import Page


# TODO: make helpers to make button registration easier
@register_page
class MainMenu(Page):
    def __init__(
        self, coordination_manager: CoordinationManager, camera: Camera
    ) -> None:
        super().__init__(coordination_manager, theme_name="main_menu", camera=camera)

    def define_initial_gui(self) -> list[ElementWrapper]:
        """Return all GUI elements for the main menu page."""

        elements: list[ElementWrapper] = []

        start_button_id = "start_button"
        start_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(100, 100, 200, 50),
            text="Start",
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="MainMenuButton", object_id=start_button_id
            ),
        )
        start_button_element = ui_element_wrapper(
            start_button, start_button_id, self.camera
        )
        elements.append(start_button_element)

        # Quit button
        quit_button_id = "quit_button"
        quit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(100, 200, 200, 50),
            text="Quit",
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="MainMenuButton", object_id=quit_button_id
            ),
        )
        quit_button_element = ui_element_wrapper(
            quit_button, quit_button_id, self.camera
        )
        elements.append(quit_button_element)

        # GUI Demo button
        gui_demo_button_id = "gui_demo_button"
        gui_demo_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(100, 300, 200, 50),
            text="Go to GUI demo",
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="MainMenuButton", object_id=gui_demo_button_id
            ),
        )
        gui_demo_element = ui_element_wrapper(
            gui_demo_button, gui_demo_button_id, self.camera
        )
        elements.append(gui_demo_element)

        # Element Demo button
        element_demo_button_id = "element_demo_button"
        element_demo_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(400, 300, 200, 50),
            text="Go to Element demo",
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="MainMenuButton", object_id=element_demo_button_id
            ),
        )
        element_demo_element = ui_element_wrapper(
            element_demo_button, element_demo_button_id, self.camera
        )
        elements.append(element_demo_element)

        return elements

    # region Input Responses

    @input_event_bind("start_button", pygame_gui.UI_BUTTON_PRESSED)
    def on_start_click(self, msg: pygame.event.Event) -> None:
        self.coordination_manager.put_message(
            PageNavigationEvent(
                action_list=[
                    (PageNavigation.CLOSE_ALL, None),
                    (PageNavigation.OPEN, "GameBoard"),
                    (PageNavigation.OPEN, "PauseButton"),
                    (PageNavigation.OPEN, "InspectHistory"),
                    # (PageNavigation.OPEN, "InspectEntity"),
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

    # endregion
