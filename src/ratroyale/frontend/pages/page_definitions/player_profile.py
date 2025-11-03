from ratroyale.coordination_manager import CoordinationManager

from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *


from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.page_registry import register_page
from ratroyale.frontend.pages.page_managers.event_binder import input_event_bind

from ratroyale.frontend.pages.page_elements.element import (
    ElementWrapper,
)
from ..page_elements.spatial_component import Camera

import pygame_gui
import pygame


@register_page
class PlayerProfile(Page):
    def __init__(
        self, coordination_manager: CoordinationManager, camera: Camera
    ) -> None:
        super().__init__(coordination_manager, camera)

    def define_initial_gui(self) -> list[ElementWrapper]:
        gui_elements: list[ElementWrapper] = []

        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 20, 100, 20),
            text="Select a Profile",
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(class_id="Header", object_id="header"),
            anchors={"centerx": "centerx", "top": "top"},
        )

        panel_element = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, 0, 450, 460),
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="MainPanel", object_id="main_panel"
            ),
            anchors={
                "centerx": "centerx",
                "centery": "centery",
            },
        )

        # === Scroll Container ===
        scroll_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(0, 0, 430, 450),
            manager=self.gui_manager,
            container=panel_element,
            allow_scroll_x=False,  # disable horizontal scroll
            anchors={
                "centerx": "centerx",
                "centery": "centery",
            },
        )

        y_offset = 10
        for i in range(4):
            pygame_gui.elements.UIImage(
                relative_rect=pygame.Rect(10, y_offset, 100, 100),
                image_surface=pygame.Surface((100, 100)),
                manager=self.gui_manager,
                container=scroll_container,
            )

            # === Name ===
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(100, y_offset + 10, 150, 25),
                text="Name",
                manager=self.gui_manager,
                container=scroll_container,
            )

            # === Info text ===
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(100, y_offset + 35, 150, 25),
                text="Info .....",
                manager=self.gui_manager,
                container=scroll_container,
            )

            # === SELECT & DELETE ===
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(150, y_offset + 65, 120, 35),
                text="SELECT",
                manager=self.gui_manager,
                container=scroll_container,
                object_id=pygame_gui.core.ObjectID(
                    class_id="SelectButton", object_id="select_button"
                ),
            )

            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(280, y_offset + 65, 120, 35),
                text="DELETE",
                manager=self.gui_manager,
                container=scroll_container,
            )
            # === Divider line ===
            divider_surface = pygame.Surface((400, 2))
            divider_surface.fill((180, 180, 180))  # light gray line
            pygame_gui.elements.UIImage(
                relative_rect=pygame.Rect(10, y_offset + 110, 390, 1),
                image_surface=divider_surface,
                manager=self.gui_manager,
                container=scroll_container,
            )

            y_offset += 120

        # === Create new profile button ===
        pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, y_offset + 10, 400, 60),
            text="+  Create new profile",
            manager=self.gui_manager,
            container=scroll_container,
            object_id=pygame_gui.core.ObjectID(
                class_id="CreateButton", object_id="create_button"
            ),
        )

        scroll_container.set_scrollable_area_dimensions((600, y_offset + 100))

        return gui_elements

    @input_event_bind("create_button", pygame_gui.UI_BUTTON_PRESSED)
    def proceed_to_create_profile(self, msg: pygame.event.Event) -> None:
        CoordinationManager.put_message(
            PageNavigationEvent(
                [
                    (PageNavigation.OPEN, "CreateProfile"),
                ]
            )
        )

    @input_event_bind("select_button", pygame_gui.UI_BUTTON_PRESSED)
    def select_button(self, msg: pygame.event.Event) -> None:
        self.close_self()
        CoordinationManager.put_message(
            PageNavigationEvent([(PageNavigation.OPEN, "MainMenu")])
        )
