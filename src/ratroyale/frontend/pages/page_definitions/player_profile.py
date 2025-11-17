from ratroyale.coordination_manager import CoordinationManager

from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *
from ratroyale.backend.player_info.player_info import SAVE_FILE_EXTENSION


from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.page_registry import register_page
from ratroyale.frontend.pages.page_managers.event_binder import input_event_bind
from ratroyale.event_tokens.input_token import get_id
from ratroyale.backend.player_info.player_info import PlayerInfo
from ratroyale.event_tokens.payloads import PlayerInfoPayload
from ratroyale.frontend.pages.page_elements.element import (
    ElementWrapper,
    ui_element_wrapper,
)
from ..page_elements.spatial_component import Camera

import pygame_gui
import pygame
from pathlib import Path

RRSAVES_DIR_PATH = Path("./saves")


@register_page
class PlayerProfile(Page):
    def __init__(
        self, coordination_manager: CoordinationManager, camera: Camera
    ) -> None:
        self.save_files: list[Path] = []
        super().__init__(coordination_manager, camera)

    def define_initial_gui(self) -> list[ElementWrapper]:
        gui_elements: list[ElementWrapper] = []
        header = ui_element_wrapper(
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(0, 20, 100, 20),
                text="Select a Profile",
                manager=self.gui_manager,
                object_id=pygame_gui.core.ObjectID(
                    class_id="Header", object_id="header"
                ),
                anchors={"centerx": "centerx", "top": "top"},
            ),
            registered_name="header",
            camera=self.camera,
        )
        gui_elements.append(header)

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
        panel_element_wrapper = ui_element_wrapper(
            panel_element, "main_panel", self.camera
        )
        gui_elements.append(panel_element_wrapper)

        # === Scroll Container ===
        scroll_panel_element = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(0, 0, 430, 450),
            manager=self.gui_manager,
            container=panel_element,
            allow_scroll_x=False,
            anchors={
                "centerx": "centerx",
                "centery": "centery",
            },
            object_id=pygame_gui.core.ObjectID(
                class_id="scoller", object_id="scroll_container_real"
            ),
        )
        scroll_panel_element_wrapper = ui_element_wrapper(
            scroll_panel_element, "scroll_container_real", self.camera
        )
        gui_elements.append(scroll_panel_element_wrapper)

        return gui_elements

    def on_open(self) -> None:
        self.save_files = [
            f for f in RRSAVES_DIR_PATH.iterdir() if f.suffix[1:] == SAVE_FILE_EXTENSION
        ]
        scroll_container_element = self._element_manager.get_element(
            "scroll_container_real"
        )
        scroll_container = scroll_container_element.get_interactable(
            pygame_gui.elements.UIScrollingContainer
        )

        y_offset = 10
        for index, save in enumerate(self.save_files):
            pygame_gui.elements.UIImage(
                relative_rect=pygame.Rect(10, y_offset, 100, 100),
                image_surface=pygame.Surface((100, 100)),
                manager=self.gui_manager,
                container=scroll_container,
            )

            # === Name ===
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(100, y_offset + 10, 150, 25),
                text=f"Name: {save.stem}",
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
                    class_id="SelectButton", object_id=f"select_button_{index}"
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
            LIGHT_GRAY = (180, 180, 180)
            divider_surface.fill(LIGHT_GRAY)
            pygame_gui.elements.UIImage(
                relative_rect=pygame.Rect(10, y_offset + 110, 390, 1),
                image_surface=divider_surface,
                manager=self.gui_manager,
                container=scroll_container,
            )

            y_offset += 120

        # === Create new profile button ===
        create_button = ui_element_wrapper(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(10, y_offset + 10, 400, 60),
                text="+  Create new profile",
                manager=self.gui_manager,
                container=scroll_container,
                object_id=pygame_gui.core.ObjectID(
                    class_id="CreateButton", object_id="create_button"
                ),
            ),
            registered_name="create_button",
            camera=self.camera,
        )

        self._element_manager.add_element(create_button)

        scroll_container.set_scrollable_area_dimensions((600, y_offset + 100))

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
        button_id = get_id(msg)
        assert button_id is not None
        button_index = int(button_id.split("_")[-1])
        selected_player_info = PlayerInfo.from_file(
            self.save_files[button_index],
        )
        assert selected_player_info is not None
        self.close_self()
        self.post(PageNavigationEvent([(PageNavigation.OPEN, "MainMenu")]))
        self.post(
            PageCallbackEvent(
                "set_player_info", payload=PlayerInfoPayload(selected_player_info)
            )
        )
