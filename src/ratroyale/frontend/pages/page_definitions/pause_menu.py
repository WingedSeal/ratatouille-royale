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
from ratroyale.frontend.pages.page_elements.spatial_component import Camera

from ..page_managers.base_page import Page


@register_page
class PauseMenu(Page):
    def __init__(
        self, coordination_manager: "CoordinationManager", camera: Camera
    ) -> None:
        super().__init__(
            coordination_manager,
            base_color=(0, 0, 0, 128),
            theme_name="pause_menu",
            camera=camera,
        )

    def define_initial_gui(self) -> list[ElementWrapper]:
        elements: list[ElementWrapper] = []

        resume_button = ui_element_wrapper(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(300, 200, 200, 50),
                text="Continue",
                manager=self.gui_manager,
                object_id=pygame_gui.core.ObjectID(
                    class_id="PauseMenuButton", object_id="resume_button"
                ),
            ),
            registered_name="resume_button",
            grouping_name="pause_menu",
            camera=self.camera,
        )
        elements.append(resume_button)

        options_button = ui_element_wrapper(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(300, 260, 200, 50),
                text="Options/Settings",
                manager=self.gui_manager,
                object_id=pygame_gui.core.ObjectID(
                    class_id="PauseMenuButton", object_id="options_button"
                ),
            ),
            registered_name="options_button",
            grouping_name="pause_menu",
            camera=self.camera,
        )
        elements.append(options_button)

        guide_button = ui_element_wrapper(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(300, 320, 200, 50),
                text="Guide Book",
                manager=self.gui_manager,
                object_id=pygame_gui.core.ObjectID(
                    class_id="PauseMenuButton", object_id="guide_button"
                ),
            ),
            registered_name="guide_button",
            grouping_name="pause_menu",
            camera=self.camera,
        )
        elements.append(guide_button)

        quit_button = ui_element_wrapper(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(300, 380, 200, 50),
                text="Quit Game",
                manager=self.gui_manager,
                object_id=pygame_gui.core.ObjectID(
                    class_id="PauseMenuButton", object_id="quit_button"
                ),
            ),
            registered_name="quit_button",
            grouping_name="pause_menu",
            camera=self.camera,
        )
        elements.append(quit_button)

        exit_desktop_button = ui_element_wrapper(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(300, 440, 200, 50),
                text="Exit to Desktop",
                manager=self.gui_manager,
                object_id=pygame_gui.core.ObjectID(
                    class_id="PauseMenuButton", object_id="exit_desktop_button"
                ),
            ),
            registered_name="exit_desktop_button",
            grouping_name="pause_menu",
            camera=self.camera,
        )
        elements.append(exit_desktop_button)

        return elements

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

    @input_event_bind("exit_desktop_button", pygame_gui.UI_BUTTON_PRESSED)
    def on_exit_desktop_click(self, msg: pygame.event.Event) -> None:
        self.coordination_manager.stop_game()
