from ratroyale.coordination_manager import CoordinationManager

from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *


from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.event_binder import input_event_bind
from ratroyale.frontend.pages.page_managers.page_registry import register_page

from ratroyale.frontend.pages.page_elements.element import (
    ElementWrapper,
    ui_element_wrapper,
)
from ..page_elements.spatial_component import Camera

import pygame_gui
import pygame


@register_page
class InspectFeature(Page):
    def __init__(
        self, coordination_manager: CoordinationManager, camera: Camera
    ) -> None:
        super().__init__(coordination_manager, camera)

    def define_initial_gui(self) -> list[ElementWrapper]:

        gui_elements: list[ElementWrapper] = []

        # === MainPanel ===
        panel_element = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(60, 70, 680, 460),
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="MainPanel", object_id="main_panel"
            ),
        )
        panel_element_wrapper = ui_element_wrapper(
            panel_element, "main_panel", self.camera
        )
        gui_elements.append(panel_element_wrapper)

        # === Close button ===
        pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(640, 12, 28, 28),
            text="x",
            manager=self.gui_manager,
            container=panel_element,
            object_id=pygame_gui.core.ObjectID(
                class_id="CloseButton", object_id="close_button"
            ),
        )

        # === Name / feature title ===
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 56, 520, 32),
            text="Name / feature title",
            manager=self.gui_manager,
            container=panel_element,
            object_id=pygame_gui.core.ObjectID(class_id="Title", object_id="title"),
            anchors={"centerx": "centerx", "top": "top"},
        )

        # === Description ===
        pygame_gui.elements.UITextBox(
            html_text="<b>Description</b><br>"
            "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            relative_rect=pygame.Rect(20, 120, 640, 120),
            manager=self.gui_manager,
            container=panel_element,
            object_id=pygame_gui.core.ObjectID(
                class_id="description", object_id="desc"
            ),
        )

        # === Skill image ===
        portrait_surface = pygame.Surface((50, 200), flags=pygame.SRCALPHA)
        portrait_surface.fill((220, 220, 255))
        pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect(0, 280, 300, 150),
            image_surface=portrait_surface,
            manager=self.gui_manager,
            container=panel_element,
            anchors={"centerx": "centerx"},
        )

        return gui_elements

    @input_event_bind("close_button", pygame_gui.UI_BUTTON_PRESSED)
    def close_panel(self, msg: pygame.event.Event) -> None:
        self.post(
            PageNavigationEvent(action_list=[(PageNavigation.CLOSE, "InspectFeature")])
        )
