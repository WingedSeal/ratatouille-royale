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
from ratroyale.frontend.pages.page_elements.element import (
    ElementWrapper,
    ui_element_wrapper,
)
from ..page_elements.spatial_component import Camera

from ratroyale.event_tokens.payloads import TurnPayload

import pygame_gui
import pygame

from pygame_gui.elements import UIPanel
from ratroyale.frontend.visual.screen_constants import SCREEN_SIZE

TURN_COUNT = 20
"""How many turn will the inspect crumb show"""


@register_page
class InspectCrumb(Page):
    def __init__(
        self, coordination_manager: CoordinationManager, camera: Camera
    ) -> None:
        super().__init__(coordination_manager, camera, is_blocking=True)

    def define_initial_gui(self) -> list[ElementWrapper]:
        gui_elements: list[ElementWrapper] = []

        # === MainPanel ===
        panel_w, panel_h = 700, 200
        panel_x = (SCREEN_SIZE[0] - panel_w) // 2
        panel_y = (SCREEN_SIZE[1] - panel_h) // 2

        panel_element = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(panel_x, panel_y, 700, 200),
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
        if turn_number < 1:
            return

        payload = TurnPayload(
            max(turn_number - TURN_COUNT // 2, 1),
            self.current_turn,
            self.current_side,
            self.crumbs_modifier,
            jump_to_turn=turn_number,
        )
        self.post(
            PageNavigationEvent(action_list=[(PageNavigation.CLOSE, "InspectCrumb")])
        )
        self.post(
            PageNavigationEvent(action_list=[(PageNavigation.OPEN, "InspectCrumb")])
        )
        self.post(PageCallbackEvent("show_crumbs", payload=payload))

    @callback_event_bind("show_crumbs")
    def update_current_turn(self, msg: PageCallbackEvent) -> None:
        payload = msg.payload
        assert isinstance(payload, TurnPayload)
        self.current_turn = payload.current_turn_number
        turn = payload.turn_number
        self.current_side = payload.current_side
        self.crumbs_modifier = payload.crumbs_modifier
        card_width = 150
        spacing = 20
        base_x = 0

        for i in range(turn, TURN_COUNT + turn):
            turn_crumbs, turn_crumbs_diff = self.crumbs_modifier.get_crumbs(
                turn, self.current_side
            )
            turn_panel = pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect(base_x, 0, card_width, 120),
                manager=self.gui_manager,
                container=self.scroll_container,
                object_id=pygame_gui.core.ObjectID(
                    class_id="TurnPanel", object_id=f"turn_{i}"
                ),
            )

            # Turn Title
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(0, 0, 150, 30),
                text=f"TURN {i}" if self.current_turn != i else f"->TURN {i}<-",
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
            if turn_crumbs_diff == 0:
                modifier_text = ""
            else:
                modifier_text = f" ({turn_crumbs_diff:+})"
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(5, 35, 50, 25),
                text=f"{turn_crumbs}{modifier_text}",
                manager=self.gui_manager,
                container=table,
            )
            turn_crumbs, turn_crumbs_diff = self.crumbs_modifier.get_crumbs(
                turn, self.current_side.other_side()
            )

            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(70, 5, 50, 25),
                text="Enemy",
                manager=self.gui_manager,
                container=table,
            )
            if turn_crumbs_diff == 0:
                modifier_text = ""
            else:
                modifier_text = f" ({turn_crumbs_diff:+})"
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(75, 35, 50, 25),
                text=f"{turn_crumbs}{modifier_text}",
                manager=self.gui_manager,
                container=table,
            )

            self.turn_panels.append(turn_panel)
            base_x += card_width + spacing

        self.scroll_container.set_scrollable_area_dimensions((base_x, 140))

        if payload.jump_to_turn is not None and self.scroll_container.horiz_scroll_bar:
            target_panel = self.turn_panels[payload.jump_to_turn - payload.turn_number]
            visible_width = self.scroll_container.relative_rect.width
            scrollable_width = (
                self.scroll_container.scrollable_container.relative_rect.width
            )

            # Center target panel in view
            center_offset = (
                target_panel.relative_rect.centerx
                - visible_width
                + target_panel.rect.width / 2
            )
            max_scroll = max(0, scrollable_width - visible_width)

            if max_scroll > 0:
                scroll_percentage = max(0, min(center_offset / max_scroll, 1))
                self.scroll_container.horiz_scroll_bar.set_scroll_from_start_percentage(
                    scroll_percentage
                )
