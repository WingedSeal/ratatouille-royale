import math
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *
from ratroyale.frontend.visual.screen_constants import SCREEN_SIZE


from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.event_binder import (
    input_event_bind,
    callback_event_bind,
)
from ratroyale.frontend.pages.page_managers.page_registry import register_page
from ratroyale.frontend.pages.page_elements.spatial_component import (
    Camera,
)
from ratroyale.frontend.pages.page_elements.element import (
    ElementWrapper,
    ui_element_wrapper,
)

import pygame_gui
import pygame

from ratroyale.event_tokens.payloads import DeckPayload


@register_page
class InspectDeckPage(Page):
    def __init__(
        self, coordination_manager: CoordinationManager, camera: Camera
    ) -> None:
        super().__init__(
            coordination_manager,
            camera,
            base_color=(0, 0, 0, 128),
        )

    def define_initial_gui(self) -> list[ElementWrapper]:
        """Return all GUI elements for the TestPage."""
        gui_elements: list[ElementWrapper] = []

        # region Card Panel + Card buttons
        deck_panel_id = "inspect_deck_panel"
        deck_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(
                100, 100, SCREEN_SIZE[0] - 200, SCREEN_SIZE[1] - 200
            ),
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="InspectDeckPanel", object_id="panel_event"
            ),
        )
        deck_panel_element = ui_element_wrapper(deck_panel, deck_panel_id, self.camera)
        gui_elements.append(deck_panel_element)

        # Nested button inside the panel
        pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                (deck_panel.relative_rect.width - 40) / 2,
                deck_panel.relative_rect.height - 50,
                100,
                40,
            ),
            text="Close",
            manager=self.gui_manager,
            container=deck_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="CloseInspectDeckButton",
                object_id="close_inspect_deck",
            ),
        )

        # endregion

        return gui_elements

    @callback_event_bind("inspect_deck")
    def show_deck(self, msg: PageCallbackEvent) -> None:
        assert isinstance(msg.payload, DeckPayload)
        deck = msg.payload.deck
        deck_panel = self._element_manager.get_element("inspect_deck_panel")
        deck_panel_object = deck_panel.get_interactable(pygame_gui.elements.UIPanel)
        scroll_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(
                0,
                0,
                deck_panel_object.relative_rect.width,
                deck_panel_object.relative_rect.height - 60,
            ),
            manager=self.gui_manager,
            allow_scroll_y=True,
            allow_scroll_x=False,
            container=deck_panel_object,
            object_id=pygame_gui.core.ObjectID(
                class_id="DeckScrollArea", object_id="deck_scroll_area"
            ),
        )
        CARD_WIDTH = 200
        CARD_HEIGHT = 70
        MARGIN = 10
        CARD_PER_ROW = max(
            (deck_panel_object.relative_rect.width - MARGIN) // (CARD_WIDTH + MARGIN), 1
        )
        ROW_COUNT = math.ceil(len(deck) / CARD_PER_ROW)
        scroll_container.set_scrollable_area_dimensions(
            (
                scroll_container.relative_rect.width,
                MARGIN + (ROW_COUNT * CARD_HEIGHT) + (ROW_COUNT * MARGIN),
            )
        )
        for card_index, squeak in enumerate(deck):
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(
                    MARGIN + card_index % CARD_PER_ROW * (CARD_WIDTH + MARGIN),
                    MARGIN + (card_index // CARD_PER_ROW) * (CARD_HEIGHT + MARGIN),
                    CARD_WIDTH,
                    CARD_HEIGHT,
                ),
                text=f"{squeak.name}",
                manager=self.gui_manager,
                container=scroll_container,
                object_id=pygame_gui.core.ObjectID(
                    class_id="Card",
                    object_id=f"card{card_index}",
                ),
            )

    @input_event_bind("close_inspect_deck", pygame_gui.UI_BUTTON_PRESSED)
    def on_close_inspect_deck_click(self, msg: pygame.event.Event) -> None:
        self.close_self()
