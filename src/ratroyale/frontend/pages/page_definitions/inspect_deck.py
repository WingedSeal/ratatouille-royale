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
from ratroyale.frontend.pages.page_elements.element_builder import (
    UIRegisterForm,
)

import pygame_gui
import pygame


@register_page
class InspectDeckPage(Page):
    def __init__(self, coordination_manager: CoordinationManager) -> None:
        super().__init__(coordination_manager, base_color=(0, 0, 0, 128))
        # if page is strangely not responsive, check is_blocking status of open pages.

    def on_open(self) -> None:
        self.post(GameManagerEvent(game_action="inspect_deck"))

    def define_initial_gui(self) -> list[UIRegisterForm]:
        """Return all GUI elements for the TestPage."""
        gui_elements: list[UIRegisterForm] = []
        # region Card Panel + Card buttons
        self.deck_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(100, 100, 600, 400),
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="InspectDeckPanel", object_id="panel_event"
            ),
        )
        gui_elements.append(UIRegisterForm("test_panel", self.deck_panel))

        # for card_index in range(56):
        #     # Nested button inside the panel
        #     pygame_gui.elements.UIButton(
        #         relative_rect=pygame.Rect(
        #             110 + card_index * 60, 110 + (card_index // 6) * 80, 50, 70
        #         ),
        #         text="image placeholder",
        #         manager=self.gui_manager,
        #         container=self.deck_panel,
        #         object_id=pygame_gui.core.ObjectID(
        #             class_id="Card",
        #             object_id=f"card{card_index}",
        #         ),
        #     )

        # endregion

        return gui_elements

    @callback_event_bind("inspect_deck")
    def show_deck(self, msg: PageCallbackEvent[list[int]]) -> None:
        deck = msg.payload
        assert deck is not None
        for card_index, card_id in enumerate(deck):
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(
                    10 + card_index * 60, 10 + (card_index // 6) * 80, 50, 70
                ),
                text="image placeholder",
                manager=self.gui_manager,
                container=self.deck_panel,
                object_id=pygame_gui.core.ObjectID(
                    class_id="Card",
                    object_id=f"card{card_index}",
                ),
            )

    # all input-listening methods will have this signature
    # e.g. def test(self, msg: pygame.event.Event) -> None:
    #   ...
    @input_event_bind("event_name", pygame_gui.UI_BUTTON_PRESSED)
    def on_example_click(self, msg: pygame.event.Event) -> None:
        button = self._element_manager.get_gui_element(
            "registered_name", pygame_gui.elements.UIButton
        )
        button.set_text("Clicked")

        # redirect or open new pages on top
        # Check out PageNavigation for available commands
        self.coordination_manager.put_message(
            PageNavigationEvent(
                action_list=[
                    (PageNavigation.OPEN, "TestCommunicate"),
                ]
            )
        )

    @input_event_bind("close_button", pygame_gui.UI_BUTTON_PRESSED)
    def close_panel(self, msg: pygame.event.Event) -> None:
        self._element_manager.remove_gui_element("test_panel")

    @input_event_bind("event_name_2", pygame_gui.UI_BUTTON_PRESSED)
    def communicate(self, msg: pygame.event.Event) -> None:
        self.coordination_manager.put_message(
            PageCallbackEvent[int]("action_name", payload=3)
        )
