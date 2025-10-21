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
from ratroyale.event_tokens.payloads import TilePayload

import pygame_gui
import pygame


@register_page
class GameInfoPage(Page):
    def __init__(
        self, coordination_manager: CoordinationManager, camera: Camera
    ) -> None:
        super().__init__(coordination_manager, camera, is_blocking=False)
        self.crumbs = 0

    def define_initial_gui(self) -> list[ElementWrapper]:
        """Return all GUI elements for the TestPage."""
        gui_elements: list[ElementWrapper] = []

        # region Perm buttons/panels
        view_deck_button_id = "view_deck_button"
        view_deck_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 450, 200, 50),
            text="View Deck",
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="ViewDeckButton",
                object_id="view_deck",
            ),
        )
        view_deck_button_element = ui_element_wrapper(
            view_deck_button, view_deck_button_id, self.camera
        )
        gui_elements.append(view_deck_button_element)

        show_crumbs_button_id = "show_crumbs_button"
        show_crumbs_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, 200, 50),
            text="Crumbs: ",
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="ShowCrumbsButton",
                object_id="show_crumbs",
            ),
        )
        show_crumbs_button_element = ui_element_wrapper(
            show_crumbs_button, show_crumbs_button_id, self.camera
        )
        gui_elements.append(show_crumbs_button_element)

        end_turn_button_id = "end_turn_button"
        end_turn_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(700, 500, 100, 50),
            text="End Turn",
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="EndTurnButton",
                object_id="end_turn",
            ),
        )
        end_turn_button_element = ui_element_wrapper(
            end_turn_button, end_turn_button_id, self.camera
        )
        gui_elements.append(end_turn_button_element)
        # end region

        # region Panels visible on hover
        tile_hover_data_panel_id = "tile_hover_data_panel"
        tile_hover_data_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(200, 0, 400, 100),
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="TileHoverDataPanel", object_id="tile_hover_data_panel"
            ),
        )
        tile_hover_data_panel_element = ui_element_wrapper(
            tile_hover_data_panel, tile_hover_data_panel_id, self.camera
        )
        gui_elements.append(tile_hover_data_panel_element)

        entity_hover_data_panel_id = "entity_hover_data_panel"
        entity_hover_data_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(200, 500, 400, 100),
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="EntityHoverDataPanel",
                object_id="entity_hover_data_panel",
            ),
        )
        entity_hover_data_panel_element = ui_element_wrapper(
            entity_hover_data_panel, entity_hover_data_panel_id, self.camera
        )
        gui_elements.append(entity_hover_data_panel_element)

        move_history_panel_id = "move_history_panel"
        move_history_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(600, 200, 200, 300),
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="MoveHistoryPanel",
                object_id="move_history_panel",
            ),
        )
        move_history_panel_element = ui_element_wrapper(
            move_history_panel, move_history_panel_id, self.camera
        )
        gui_elements.append(move_history_panel_element)
        # end region

        return gui_elements

    def on_open(self) -> None:
        show_crumbs_button = self._element_manager.get_element_wrapper(
            "show_crumbs_button", "UI_ELEMENT"
        )
        show_crumbs_button.get_interactable(pygame_gui.elements.UIButton).set_text(
            f"Crumbs: {self.crumbs}"
        )

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
    def on_tile_hover(self, msg: PageCallbackEvent[ElementWrapper]) -> None:
        received_element = msg.payload
        if received_element is None or not isinstance(received_element, ElementWrapper):
            return

        tile_hover_data_panel = self._element_manager.get_element_wrapper(
            "tile_hover_data_panel", "UI_ELEMENT"
        )
        entity_hover_data_panel = self._element_manager.get_element_wrapper(
            "entity_hover_data_panel", "UI_ELEMENT"
        )

        tile_hover_data_panel_object = tile_hover_data_panel.get_interactable(
            pygame_gui.elements.UIPanel
        )
        entity_hover_data_panel_object = entity_hover_data_panel.get_interactable(
            pygame_gui.elements.UIPanel
        )

        if isinstance(received_element.payload, TilePayload):
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(0, 0, 100, 20),
                text=f"Odd-R: {received_element.payload.tile.coord}",
                manager=self.gui_manager,
                container=tile_hover_data_panel_object,
                object_id=pygame_gui.core.ObjectID(
                    class_id="OddRCoordButton",
                    object_id="odd_r_coord_button",
                ),
            )

            for index, feature in enumerate(received_element.payload.tile.features):
                pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(100 + index * 60, (index // 6), 50, 20),
                    text=f"{feature.FEATURE_ID()}",
                    manager=self.gui_manager,
                    container=tile_hover_data_panel_object,
                    object_id=pygame_gui.core.ObjectID(
                        class_id="ShowFeatureButton",
                        object_id=f"ShowFeatureButton{index}",
                    ),
                )
            for index, entity in enumerate(received_element.payload.tile.entities):
                pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(
                        10 + index * 60, 10 + (index // 6) * 80, 50, 20
                    ),
                    text=f"{entity.name}",
                    manager=self.gui_manager,
                    container=entity_hover_data_panel_object,
                    object_id=pygame_gui.core.ObjectID(
                        class_id="ShowEntityButton",
                        object_id=f"ShowEntityButton{index}",
                    ),
                )

    @callback_event_bind("move_history")
    def _move_history(self, msg: PageCallbackEvent[list[str]]) -> None:
        move_history_panel = self._element_manager.get_element_wrapper(
            "move_history_panel", "UI_ELEMENT"
        )
        move_history_panel_object = move_history_panel.get_interactable(
            pygame_gui.elements.UIPanel
        )
        pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, 100, 20),
            text="dummy button for move history panel",
            manager=self.gui_manager,
            container=move_history_panel_object,
            object_id=pygame_gui.core.ObjectID(
                class_id="OddRCoordButton",
                object_id="odd_r_coord_button",
            ),
        )
        # TODO: add more buttons when receiving successful move history events
        ...
