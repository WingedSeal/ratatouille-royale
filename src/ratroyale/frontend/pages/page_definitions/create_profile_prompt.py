from ratroyale.coordination_manager import CoordinationManager

from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *
from ratroyale.game_data import RRSAVES_DIR_PATH


from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.page_registry import register_page
from ratroyale.frontend.pages.page_managers.event_binder import input_event_bind

from ratroyale.frontend.pages.page_elements.element import (
    ElementWrapper,
    ui_element_wrapper,
)
from ..page_elements.spatial_component import Camera

from ratroyale.backend.player_info.preset_player_info import get_default_player_info

import pygame_gui
import pygame

from ratroyale.backend.player_info.player_info import SAVE_FILE_EXTENSION


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
        title_label = ui_element_wrapper(
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(0, 10, 420, 40),
                text="Enter your name",
                manager=self.gui_manager,
                container=panel_element,
                object_id=pygame_gui.core.ObjectID(
                    class_id="TitleLabel", object_id="title_label"
                ),
                anchors={"centerx": "centerx", "top": "top"},
            ),
            registered_name="title_label",
            camera=self.camera,
        )
        gui_elements.append(title_label)

        # === Text entry box ===
        name_entry = ui_element_wrapper(
            pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect(0, 0, 240, 40),
                manager=self.gui_manager,
                container=panel_element,
                object_id=pygame_gui.core.ObjectID(
                    class_id="NameEntry", object_id="name_entry"
                ),
                anchors={"center": "center"},
            ),
            registered_name="name_entry",
            camera=self.camera,
        )
        gui_elements.append(name_entry)

        # === Cancel button ===
        cancel_button = ui_element_wrapper(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(40, 100, 100, 40),
                text="Cancel",
                manager=self.gui_manager,
                container=panel_element,
                object_id=pygame_gui.core.ObjectID(
                    class_id="CancelButton", object_id="cancel_button"
                ),
            ),
            registered_name="cancel_button",
            camera=self.camera,
        )
        gui_elements.append(cancel_button)

        # === Confirm button ===
        confirm_button = ui_element_wrapper(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(175, 100, 100, 40),
                text="Confirm",
                manager=self.gui_manager,
                container=panel_element,
                object_id=pygame_gui.core.ObjectID(
                    class_id="ConfirmButton", object_id="confirm_button"
                ),
            ),
            registered_name="confirm_button",
            camera=self.camera,
        )
        gui_elements.append(confirm_button)
        return gui_elements

    @input_event_bind("confirm_button", pygame_gui.UI_BUTTON_PRESSED)
    def confirm_profile(self, msg: pygame.event.Event) -> None:
        ui_text_entry_line_element = self._element_manager.get_element("name_entry")
        ui_text_entry_line = ui_text_entry_line_element.get_interactable(
            pygame_gui.elements.UITextEntryLine
        )
        text = ui_text_entry_line.get_text().strip()
        get_default_player_info().to_file(
            RRSAVES_DIR_PATH / f"{text}.{SAVE_FILE_EXTENSION}"
        )
        self.close_self()
        self.close_page("PlayerProfile")
        self.open_page("PlayerProfile")

    @input_event_bind("cancel_button", pygame_gui.UI_BUTTON_PRESSED)
    def cancel_button(self, msg: pygame.event.Event) -> None:
        self.close_self()
