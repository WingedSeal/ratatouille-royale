from ratroyale.coordination_manager import CoordinationManager

from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *


from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.page_registry import register_page
from ratroyale.frontend.pages.page_managers.event_binder import input_event_bind

from ratroyale.frontend.pages.page_elements.element import (
    ElementWrapper,
    ui_element_wrapper,
)
from ..page_elements.spatial_component import Camera

import pygame_gui
import pygame


@register_page
class CreateProfile(Page):
    def __init__(
        self, coordination_manager: CoordinationManager, camera: Camera
    ) -> None:
        super().__init__(coordination_manager, camera)

    def define_initial_gui(self) -> list[ElementWrapper]:
        gui_elements: list[ElementWrapper] = []

        panel_element = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, 0, 320, 160),
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="MainPanel", object_id="main_panel"
            ),
            anchors={
                "centerx": "centerx",
                "centery": "centery",
            },
        )
        panel_element_wrapper = ui_element_wrapper(
            panel_element, "main_panel", self.camera
        )
        gui_elements.append(panel_element_wrapper)

        # === Title label ===
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 10, 420, 40),
            text="Enter your name",
            manager=self.gui_manager,
            container=panel_element,
            object_id=pygame_gui.core.ObjectID(
                class_id="TitleLabel", object_id="title_label"
            ),
            anchors={"centerx": "centerx", "top": "top"},
        )

        # === Text entry box ===
        pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(0, 0, 240, 40),
            manager=self.gui_manager,
            container=panel_element,
            object_id=pygame_gui.core.ObjectID(
                class_id="NameEntry", object_id="name_entry"
            ),
            anchors={"center": "center"},
        )

        # === Cancel button ===
        pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(40, 100, 100, 40),
            text="Cancel",
            manager=self.gui_manager,
            container=panel_element,
            object_id=pygame_gui.core.ObjectID(
                class_id="CancelButton", object_id="cancel_button"
            ),
        )

        # === Confirm button ===
        pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(175, 100, 100, 40),
            text="Confirm",
            manager=self.gui_manager,
            container=panel_element,
            object_id=pygame_gui.core.ObjectID(
                class_id="ConfirmButton", object_id="confirm_button"
            ),
        )
        return gui_elements

    @input_event_bind("confirm_button", pygame_gui.UI_BUTTON_PRESSED)
    def confirm_profile(self, msg: pygame.event.Event) -> None:
        self.close_self()

    @input_event_bind("cancel_button", pygame_gui.UI_BUTTON_PRESSED)
    def cancel_button(self, msg: pygame.event.Event) -> None:
        self.close_self()
