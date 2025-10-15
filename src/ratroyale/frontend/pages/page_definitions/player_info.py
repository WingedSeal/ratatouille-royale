from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *


from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.event_binder import input_event_bind
from ratroyale.frontend.pages.page_managers.page_registry import register_page

from ratroyale.frontend.pages.page_elements.element_builder import (
    UIRegisterForm,
)

import pygame_gui
import pygame


@register_page
class PlayerInfoPage(Page):
    def __init__(self, coordination_manager: CoordinationManager) -> None:
        super().__init__(coordination_manager)
        # if page is strangely not responsive, check is_blocking status of open pages.
        # self.crumbs = 0

    def define_initial_gui(self) -> list[UIRegisterForm]:
        """Return all GUI elements for the TestPage."""
        gui_elements: list[UIRegisterForm] = []

        # region Panel + nested button
        # feature_data_panel = pygame_gui.elements.UIPanel(
        #     relative_rect=pygame.Rect(0, 0, 800, 600),
        #     manager=self.gui_manager,
        #     object_id=pygame_gui.core.ObjectID(
        #         class_id="InfoPanel", object_id="panel_event"
        #     ),
        # )
        # gui_elements.append(UIRegisterForm("player_info_panel", feature_data_panel))

        # entity_data_panel = pygame_gui.elements.UIPanel(
        #     relative_rect=pygame.Rect(0, 0, 800, 600),
        #     manager=self.gui_manager,
        #     object_id=pygame_gui.core.ObjectID(
        #         class_id="InfoPanel", object_id="panel_event"
        #     ),
        # )
        # gui_elements.append(UIRegisterForm("player_info_panel", entity_data_panel))

        # Nested button inside the panel
        # pygame_gui.elements.UIButton(
        #     relative_rect=pygame.Rect(0, 30, 150, 30),
        #     text=f"Crumbs: {0}",
        #     manager=self.gui_manager,
        #     container=panel_element,
        #     object_id=pygame_gui.core.ObjectID(
        #         class_id="CrumbsButton", object_id="crumbs_button"
        #     ),
        # )
        # endregion

        # region Other buttons
        gui_elements.append(
            UIRegisterForm(
                "view_deck_button",  # <- registered name. for getting & deleting.
                pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(0, 450, 200, 50),
                    text="View Deck",
                    manager=self.gui_manager,
                    object_id=pygame_gui.core.ObjectID(
                        class_id="ViewDeckButton",  # <- theming name.
                        object_id="view_deck",  # <- event name. used for listening.
                    ),
                ),
            )
        )

        # gui_elements.append(
        #     UIRegisterForm(
        #         "registered_name_2",  # <- registered name. for getting & deleting.
        #         pygame_gui.elements.UIButton(
        #             relative_rect=pygame.Rect(400, 100, 200, 50),
        #             text="Test Button",
        #             manager=self.gui_manager,
        #             object_id=pygame_gui.core.ObjectID(
        #                 class_id="whatever",  # <- theming name.
        #                 object_id="event_name_2",  # <- event name. used for listening.
        #             ),
        #         ),
        #     )
        # )
        # endregion

        # All elements returned here are automatically registered at the start of page.
        return gui_elements

    # all input-listening methods will have this signature
    # e.g. def test(self, msg: pygame.event.Event) -> None:
    #   ...
    @input_event_bind("view_deck", pygame_gui.UI_BUTTON_PRESSED)
    def on_view_deck_click(self, msg: pygame.event.Event) -> None:
        # button = self._element_manager.get_gui_element(
        #     "view_deck_button", pygame_gui.elements.UIButton
        # )

        # redirect or open new pages on top
        # Check out PageNavigation for available commands
        self.coordination_manager.put_message(
            PageNavigationEvent(
                action_list=[
                    (PageNavigation.OPEN, "InspectDeckPage"),
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
