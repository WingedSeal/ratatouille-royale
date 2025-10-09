from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.input_token import InputManagerEvent
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *

from ratroyale.frontend.gesture.gesture_data import GestureType

from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.event_binder import input_event_bind
from ratroyale.frontend.pages.page_managers.page_registry import register_page

from ratroyale.frontend.pages.page_elements.element_builder import (
    ElementConfig,
    UIRegisterForm,
)

import pygame_gui
import pygame


@register_page
class TestPage(Page):
    def __init__(self, coordination_manager: CoordinationManager) -> None:
        super().__init__(coordination_manager)
        # if page is strangely not responsive, check is_blocking status of open pages.

    def define_initial_gui(self) -> list[UIRegisterForm]:
        """Return all GUI elements for the TestPage."""
        gui_elements: list[UIRegisterForm] = []

        # region Panel + nested button
        panel_element = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, 0, 400, 300),
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="AbilityPanel", object_id="panel_event"
            ),
        )
        gui_elements.append(UIRegisterForm("test_panel", panel_element))

        # Nested button inside the panel
        pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 30, 150, 30),
            text="test btn",
            manager=self.gui_manager,
            container=panel_element,
            object_id=pygame_gui.core.ObjectID(
                class_id="AbilityButton", object_id="close_button"
            ),
        )
        # endregion

        # region Other buttons
        gui_elements.append(
            UIRegisterForm(
                "registered_name",  # <- registered name. for getting & deleting.
                pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(200, 100, 200, 50),
                    text="Test Button",
                    manager=self.gui_manager,
                    object_id=pygame_gui.core.ObjectID(
                        class_id="whatever",  # <- theming name.
                        object_id="event_name",  # <- event name. used for listening.
                    ),
                ),
            )
        )

        gui_elements.append(
            UIRegisterForm(
                "registered_name_2",  # <- registered name. for getting & deleting.
                pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(400, 100, 200, 50),
                    text="Test Button",
                    manager=self.gui_manager,
                    object_id=pygame_gui.core.ObjectID(
                        class_id="whatever",  # <- theming name.
                        object_id="event_name_2",  # <- event name. used for listening.
                    ),
                ),
            )
        )
        # endregion

        # All elements returned here are automatically registered at the start of page.
        return gui_elements

    # all input-listening methods will have this signature
    # e.g. def test(self, msg: pygame.event.Event) -> None:
    #   ...
    @input_event_bind("event_name", pygame_gui.UI_BUTTON_PRESSED)
    def on_example_click(self, msg: pygame.event.Event) -> None:
        print("test button clicked")
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
        print("closing panel")
        self._element_manager.remove_gui_element("test_panel")

    @input_event_bind("event_name_2", pygame_gui.UI_BUTTON_PRESSED)
    def communicate(self, msg: pygame.event.Event) -> None:
        print("communication")
        self.coordination_manager.put_message(
            PageCallbackEvent[int]("action_name", payload=3)
        )
