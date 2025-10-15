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
from ratroyale.backend.tile import Tile
from ratroyale.backend.entity import Entity
from ratroyale.frontend.pages.page_elements.element import Element


import pygame_gui
import pygame


@register_page
class PlayerInfoPage(Page):
    def __init__(self, coordination_manager: CoordinationManager) -> None:
        super().__init__(coordination_manager, is_blocking=False)
        self.crumbs = 0

    def define_initial_gui(self) -> list[UIRegisterForm]:
        """Return all GUI elements for the TestPage."""
        gui_elements: list[UIRegisterForm] = []

        # region Permanent buttons/panels
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

        gui_elements.append(
            UIRegisterForm(
                "show_crumbs_button",
                pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(0, 0, 200, 50),
                    text="Crumbs: ",
                    manager=self.gui_manager,
                    object_id=pygame_gui.core.ObjectID(
                        class_id="ShowCrumbsButton",
                        object_id="show_crumbs",
                    ),
                ),
            )
        )

        gui_elements.append(
            UIRegisterForm(
                "end_turn_button",
                pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(700, 500, 100, 50),
                    text="End Turn",
                    manager=self.gui_manager,
                    object_id=pygame_gui.core.ObjectID(
                        class_id="EndTurnButton",
                        object_id="end_turn",
                    ),
                ),
            )
        )

        # end region

        # region Panels visible on hover
        gui_elements.append(
            UIRegisterForm(
                "tile_hover_data_panel",
                pygame_gui.elements.UIPanel(
                    relative_rect=pygame.Rect(200, 0, 400, 100),
                    manager=self.gui_manager,
                    object_id=pygame_gui.core.ObjectID(
                        class_id="TileHoverDataPanel", object_id="tile_hover_data_panel"
                    ),
                ),
            )
        )

        gui_elements.append(
            UIRegisterForm(
                "entity_hover_data_panel",
                pygame_gui.elements.UIPanel(
                    relative_rect=pygame.Rect(200, 500, 400, 100),
                    manager=self.gui_manager,
                    object_id=pygame_gui.core.ObjectID(
                        class_id="EntityHoverDataPanel",
                        object_id="entity_hover_data_panel",
                    ),
                ),
            )
        )

        # end region

        return gui_elements

    def on_open(self) -> None:
        show_crumbs_button = self._element_manager.get_gui_element(
            "show_crumbs_button", pygame_gui.elements.UIButton
        )
        show_crumbs_button.set_text(f"Crumbs: {self.crumbs}")

    @input_event_bind("view_deck", pygame_gui.UI_BUTTON_PRESSED)
    def on_view_deck_click(self, msg: pygame.event.Event) -> None:
        self.coordination_manager.put_message(
            PageNavigationEvent(
                action_list=[
                    (PageNavigation.OPEN, "InspectDeckPage"),
                ]
            )
        )

    @input_event_bind("end_turn", pygame_gui.UI_BUTTON_PRESSED)
    def on_end_turn_click(self, msg: pygame.event.Event) -> None:
        self.coordination_manager.put_message(
            GameManagerEvent(game_action="end_turn", payload=None)
        )

    @callback_event_bind("tile_hover")
    def on_tile_hover(self, msg: PageCallbackEvent[Element[Tile | Entity]]) -> None:
        received_element = msg.payload
        if received_element is None or not isinstance(received_element, Element):
            return

        tile_hover_data_panel = self._element_manager.get_gui_element(
            "tile_hover_data_panel", pygame_gui.elements.UIPanel
        )
        entity_hover_data_panel = self._element_manager.get_gui_element(
            "entity_hover_data_panel", pygame_gui.elements.UIPanel
        )

        if isinstance(received_element.payload, Tile):
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(0, 0, 100, 20),
                text=f"Odd-R: {received_element.payload.coord}",
                manager=self.gui_manager,
                container=tile_hover_data_panel,
                object_id=pygame_gui.core.ObjectID(
                    class_id="OddRCoordButton",
                    object_id="odd_r_coord_button",
                ),
            )

            for index, feature in enumerate(received_element.payload.features):
                pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(100 + index * 60, (index // 6), 50, 20),
                    text=f"{feature.FEATURE_ID()}",
                    manager=self.gui_manager,
                    container=tile_hover_data_panel,
                    object_id=pygame_gui.core.ObjectID(
                        class_id="ShowFeatureButton",
                        object_id=f"ShowFeatureButton{index}",
                    ),
                )
            for index, entity in enumerate(received_element.payload.entities):
                pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(
                        10 + index * 60, 10 + (index // 6) * 80, 50, 20
                    ),
                    text=f"{entity.name}",
                    manager=self.gui_manager,
                    container=entity_hover_data_panel,
                    object_id=pygame_gui.core.ObjectID(
                        class_id="ShowEntityButton",
                        object_id=f"ShowEntityButton{index}",
                    ),
                )

    # @input_event_bind("close_button", pygame_gui.UI_BUTTON_PRESSED)
    # def close_panel(self, msg: pygame.event.Event) -> None:
    #     self._element_manager.remove_gui_element("test_panel")

    # @input_event_bind("event_name_2", pygame_gui.UI_BUTTON_PRESSED)
    # def communicate(self, msg: pygame.event.Event) -> None:
    #     self.coordination_manager.put_message(
    #         PageCallbackEvent[int]("action_name", payload=3)
    #     )
