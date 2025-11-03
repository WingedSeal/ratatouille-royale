from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *


from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.event_binder import (
    input_event_bind,
    callback_event_bind,
)
from ratroyale.frontend.pages.page_managers.page_registry import register_page
from ratroyale.backend.game_manager import crumb_per_turn
from ratroyale.frontend.pages.page_elements.element import (
    ElementWrapper,
    ui_element_wrapper,
)
from ..page_elements.spatial_component import Camera

from ratroyale.event_tokens.payloads import TurnPayload

import pygame_gui
import pygame

from pygame_gui.elements import UIPanel


@register_page
class InspectCrumb(Page):
    def __init__(
        self, coordination_manager: CoordinationManager, camera: Camera
    ) -> None:
        super().__init__(coordination_manager, camera, is_blocking=True)

    def define_initial_gui(self) -> list[ElementWrapper]:
        gui_elements: list[ElementWrapper] = []

        # === MainPanel ===
        panel_element = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(50, 255, 700, 200),
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="MainPanel", object_id="main_panel"
            ),
        )
        panel_element_wrapper = ui_element_wrapper(
            panel_element, "main_panel", self.camera
        )
        gui_elements.append(panel_element_wrapper)

        # === Crumbs Title ===
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(300, 10, 100, 30),
            text="Crumbs",
            manager=self.gui_manager,
            container=panel_element,
            object_id=pygame_gui.core.ObjectID(
                class_id="CrumbTitle", object_id="crumb_title"
            ),
        )

        # === Close button ===
        pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(650, 10, 30, 30),
            text="X",
            manager=self.gui_manager,
            container=panel_element,
            object_id=pygame_gui.core.ObjectID(
                class_id="CloseButton", object_id="close_button"
            ),
        )

        # === Search button ===
        self.search_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(100, 10, 55, 30),
            text="Search",
            manager=self.gui_manager,
            container=panel_element,
            object_id=pygame_gui.core.ObjectID(
                class_id="SearchButton", object_id="search_button"
            ),
        )

        # === Text Input ===
        self.input_box = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(10, 10, 90, 30),
            manager=self.gui_manager,
            container=panel_element,
            object_id=pygame_gui.core.ObjectID(
                class_id="TextInput", object_id="text_input_box"
            ),
        )

        # === Scrolling Container ===
        self.scroll_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(10, 50, 680, 140),
            manager=self.gui_manager,
            container=panel_element,
            object_id=pygame_gui.core.ObjectID(
                class_id="TurnScroll", object_id="turn_scroll"
            ),
            allow_scroll_x=True,
            allow_scroll_y=False,
        )

        # === Multiple turn panels ===
        self.turn_panels: list[UIPanel] = []

        return gui_elements

    @input_event_bind("close_button", pygame_gui.UI_BUTTON_PRESSED)
    def close_panel(self, msg: pygame.event.Event) -> None:
        self.post(
            PageNavigationEvent(action_list=[(PageNavigation.CLOSE, "InspectCrumb")])
        )

    @input_event_bind("search_button", pygame_gui.UI_BUTTON_PRESSED)
    def search_turn(self, msg: pygame.event.Event) -> None:
        """Jump instantly to the specified turn (no scrollbar sync)."""
        text = self.input_box.get_text().strip()
        if not text.isdigit():
            return  # ignore invalid input

        turn_number = int(text)
        if not (1 <= turn_number <= len(self.turn_panels)):
            return

        # --- find the target turn panel ---
        scrollable_surface = self.scroll_container.scrollable_container
        visible_width = self.scroll_container.relative_rect.width

        target_panel = self.turn_panels[turn_number - 1]
        panel_x = target_panel.relative_rect.x
        panel_w = target_panel.relative_rect.width

        # --- compute offset so that target is centered in view ---
        new_scroll_x = panel_x + panel_w / 2 - visible_width / 2

        # clamp within valid range
        max_scroll = max(0, scrollable_surface.relative_rect.width - visible_width)
        new_scroll_x = max(0, min(new_scroll_x, max_scroll))

        # --- move the inner container (jump instantly) ---
        scrollable_surface.set_relative_position((-new_scroll_x, 0))

    @callback_event_bind("show_crumbs")
    def update_current_turn(self, msg: PageCallbackEvent) -> None:
        payload = msg.payload
        assert isinstance(payload, TurnPayload)
        self.current_turn = payload.turn_number
        turn_count = 20
        card_width = 150
        spacing = 20
        base_x = 0

        for i in range(self.current_turn, turn_count + self.current_turn):
            turn_crumbs = crumb_per_turn(i)
            turn_panel = pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect(base_x, 0, card_width, 120),
                manager=self.gui_manager,
                container=self.scroll_container,
                object_id=pygame_gui.core.ObjectID(
                    class_id="TurnPanel", object_id=f"turn_{i+1}"
                ),
            )

            # Turn Title
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(0, 0, 150, 30),
                text=f"TURN {i+1}",
                manager=self.gui_manager,
                container=turn_panel,
                anchors={"centerx": "centerx"},
            )

            # Table (You vs Enemy)
            table = pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect(8, 35, 130, 70),
                manager=self.gui_manager,
                container=turn_panel,
            )

            pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect(60, 5, 2, 60),
                manager=self.gui_manager,
                container=table,
            )

            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(5, 5, 50, 25),
                text="You",
                manager=self.gui_manager,
                container=table,
            )
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(5, 35, 50, 25),
                text=f"{turn_crumbs}",
                manager=self.gui_manager,
                container=table,
            )
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(70, 5, 50, 25),
                text="Enemy",
                manager=self.gui_manager,
                container=table,
            )
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(75, 35, 50, 25),
                text=f"{turn_crumbs}",
                manager=self.gui_manager,
                container=table,
            )

            self.turn_panels.append(turn_panel)
            base_x += card_width + spacing

        self.scroll_container.set_scrollable_area_dimensions((base_x, 140))
