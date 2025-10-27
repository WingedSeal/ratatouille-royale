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
from ratroyale.frontend.pages.page_elements.spatial_component import (
    Camera,
)
from ratroyale.frontend.pages.page_elements.element import (
    ElementWrapper,
    ui_element_wrapper,
)

import pygame_gui
import pygame


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

    def on_open(self) -> None:
        self.post(GameManagerEvent(game_action="inspect_deck"))

    def define_initial_gui(self) -> list[ElementWrapper]:
        """Return all GUI elements for the TestPage."""
        gui_elements: list[ElementWrapper] = []

        # region Card Panel + Card buttons
        deck_panel_id = "inspect_deck_panel"
        deck_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(100, 100, 600, 400),
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="InspectDeckPanel", object_id="panel_event"
            ),
        )
        deck_panel_element = ui_element_wrapper(deck_panel, deck_panel_id, self.camera)
        gui_elements.append(deck_panel_element)

        # Nested button inside the panel
        pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(250, 350, 100, 40),
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
        deck = msg.payload
        deck_panel = self._element_manager.get_element("inspect_deck_panel")
        deck_panel_object = deck_panel.get_interactable(pygame_gui.elements.UIPanel)
        assert deck is not None
        for card_index, card_id in enumerate(deck):  # type: ignore
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(
                    10 + card_index * 60, 10 + (card_index // 6) * 80, 50, 70
                ),
                text="image placeholder",
                manager=self.gui_manager,
                container=deck_panel_object,
                object_id=pygame_gui.core.ObjectID(
                    class_id="Card",
                    object_id=f"card{card_index}",
                ),
            )

    @input_event_bind("close_inspect_deck", pygame_gui.UI_BUTTON_PRESSED)
    def on_example_click(self, msg: pygame.event.Event) -> None:
        self.close_self()
