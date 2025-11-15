from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.payloads import MoveHistoryPayload, FeaturePayload

from ratroyale.event_tokens.input_token import get_id
from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.event_binder import (
    input_event_bind,
    callback_event_bind,
    game_event_bind,
)
from ratroyale.frontend.pages.page_managers.page_registry import register_page
from ratroyale.frontend.pages.page_elements.spatial_component import (
    Camera,
)
from ratroyale.frontend.pages.page_elements.element import (
    ElementWrapper,
    ui_element_wrapper,
)
from ratroyale.event_tokens.payloads import (
    TilePayload,
    GameSetupPayload,
    EntityPayload,
    CrumbUpdatePayload,
)
from ratroyale.backend.tile import Tile
from ratroyale.backend.game_event import CrumbChangeEvent, EntityMoveEvent, EndTurnEvent
from ratroyale.backend.side import Side
from ratroyale.backend.feature import Feature

import pygame_gui
import pygame


@register_page
class GameInfoPage(Page):
    def __init__(
        self, coordination_manager: CoordinationManager, camera: Camera
    ) -> None:
        super().__init__(coordination_manager, camera, is_blocking=False)
        self.crumbs = 0
        self.temp_saved_buttons: list[str] = []
        self.temp_selected_tile: Tile | None = None
        self.temp_hovered_tile: Tile | None = None
        self.move_history: list[dict[str, str | int | Side | None]] = []
        self.current_turn: int = 1
        self.current_turn_side: Side | None = None
        self.player_side: Side | None = None
        self.move_history_buttons: list[str] = []
        self.button_move_data: dict[str, dict[str, str | int | Side | None]] = {}
        self.button_feature_data: dict[str, Feature] = {}

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
            relative_rect=pygame.Rect(200, 0, 400, 50),
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

    @game_event_bind(CrumbChangeEvent)
    def crumb_change_event(self, event: CrumbChangeEvent) -> None:
        self.crumbs = event.new_crumbs
        show_crumbs_button = self._element_manager.get_element("show_crumbs_button")
        show_crumbs_button.get_interactable(pygame_gui.elements.UIButton).set_text(
            f"Crumbs: {self.crumbs}"
        )

    @callback_event_bind("start_game")
    def start_game(self, msg: PageCallbackEvent) -> None:
        if msg.success and msg.payload:
            payload = msg.payload
            assert isinstance(payload, GameSetupPayload)
            show_crumbs_button = self._element_manager.get_element("show_crumbs_button")
            show_crumbs_button.get_interactable(pygame_gui.elements.UIButton).set_text(
                f"Crumbs: {payload.starting_crumbs}"
            )
            self.crumbs = payload.starting_crumbs
            # Store player side for tracking turns
            self.player_side = payload.player_1_side

    @callback_event_bind("tile_selected")
    def tile_selected(self, msg: PageCallbackEvent) -> None:
        if msg.success and msg.payload:
            payload = msg.payload
            assert isinstance(payload, TilePayload)
            self.temp_selected_tile = payload.tile

            self.kill_old_tile_data()
            self.update_entity_info(self.temp_selected_tile)
            self.update_tile_info(self.temp_selected_tile)

    @callback_event_bind("tile_deselected")
    def tile_deselected(self, msg: PageCallbackEvent) -> None:
        if msg.success:
            self.temp_selected_tile = None
            self.kill_old_tile_data()

    @input_event_bind("view_deck", pygame_gui.UI_BUTTON_PRESSED)
    def on_view_deck_click(self, msg: pygame.event.Event) -> None:
        self.post(
            PageNavigationEvent(
                action_list=[
                    (PageNavigation.OPEN, "InspectDeckPage"),
                ]
            )
        )

    @input_event_bind("end_turn", pygame_gui.UI_BUTTON_PRESSED)
    def on_end_turn_click(self, msg: pygame.event.Event) -> None:
        self.post(GameManagerEvent(game_action="end_turn", payload=None))

    @callback_event_bind("tile_hovered")
    def on_tile_hover(self, msg: PageCallbackEvent) -> None:
        # If the player has already clicked on a tile, stop hover from changing the shown info.
        if self.temp_selected_tile:
            return

        if msg.success and msg.payload:
            payload = msg.payload
            assert isinstance(payload, TilePayload)

            # Kill old buttons to refresh the panels
            self.kill_old_tile_data()

            # Change tile to display
            self.temp_hovered_tile = payload.tile
            self.update_entity_info(self.temp_hovered_tile)
            self.update_tile_info(self.temp_hovered_tile)

    @callback_event_bind("no_hovered")
    def no_hovered(self, msg: PageCallbackEvent) -> None:
        self.temp_hovered_tile = None
        if not self.temp_selected_tile:
            self.kill_old_tile_data()

    @game_event_bind(EntityMoveEvent)
    def on_entity_move(self, event: EntityMoveEvent) -> None:
        """Track entity movements in move history."""
        move_entry: dict[str, str | int | Side | None] = {
            "entity_name": event.entity.name,
            "from_pos": str(event.from_pos),
            "to_pos": str(event.path[-1]),
            "turn": self.current_turn,
            "side": event.entity.side,
        }
        self.move_history.append(move_entry)
        self._refresh_move_history_panel()

    @game_event_bind(EndTurnEvent)
    def on_end_turn(self, event: EndTurnEvent) -> None:
        """Track turn changes."""
        self.current_turn_side = event.to_side
        self.current_turn += 1
        self._refresh_move_history_panel()

    @callback_event_bind("move_history")
    def _move_history(self, msg: PageCallbackEvent) -> None:
        """Callback for manual move history refresh if needed."""
        self._refresh_move_history_panel()

    @input_event_bind("move_history_btn", pygame_gui.UI_BUTTON_PRESSED)
    def on_move_history_click(self, msg: pygame.event.Event) -> None:
        """Handle click on move history button to show inspect history."""
        button_id = (
            msg.ui_element.object_ids[1] if len(msg.ui_element.object_ids) > 1 else None
        )
        if button_id and button_id in self.button_move_data:
            move_data = self.button_move_data[button_id]
            turn_value = move_data["turn"]
            assert isinstance(turn_value, int), "turn must be an int"
            payload = MoveHistoryPayload(
                entity_name=str(move_data["entity_name"]),
                from_pos=str(move_data["from_pos"]),
                to_pos=str(move_data["to_pos"]),
                turn=turn_value,
                # is_player_1_move=(move_data["side"] == self.player_side),
            )
            self.post(PageNavigationEvent([(PageNavigation.OPEN, "InspectHistory")]))
            self.post(PageCallbackEvent("move_history_data", payload=payload))

    @input_event_bind("feature_btn", pygame_gui.UI_BUTTON_PRESSED)
    def on_feature_button_click(self, msg: pygame.event.Event) -> None:
        """Handle feature button click to show feature details."""
        button_id = (
            msg.ui_element.object_ids[1] if len(msg.ui_element.object_ids) > 1 else None
        )

        if button_id and button_id in self.button_feature_data:
            feature = self.button_feature_data[button_id]

            feature_name, feature_description = feature.get_name_and_description()
            description_parts: list[str] = [feature_description]

            if feature.health is not None:
                description_parts.append(f"Health: {feature.health}")

            if feature.defense is not None:
                description_parts.append(f"Defense: {feature.defense}")

            description_parts.append(
                f"Collision: {'Yes' if feature.is_collision() else 'No'}"
            )

            if feature.side is not None:
                description_parts.append(f"Side: {feature.side}")

            feature_full_description = "\n".join(description_parts)

            payload = FeaturePayload(
                feature_name=feature_name,
                feature_description=feature_full_description,
                feature_type=type(feature).__name__,
            )

            self.post(PageNavigationEvent([(PageNavigation.OPEN, "InspectFeature")]))
            self.post(PageCallbackEvent("feature_data", payload=payload))

    # region UTILITIES

    def update_entity_info(self, tile: Tile) -> None:
        entity_hover_data_panel = self._element_manager.get_element(
            "entity_hover_data_panel"
        )
        entity_hover_data_panel_object = entity_hover_data_panel.get_interactable(
            pygame_gui.elements.UIPanel
        )
        new_element_wrappers = []
        for index, entity in enumerate(tile.entities):
            entity_button_id = f"ShowEntityButton_{index}"
            entity_button_wrapper = ui_element_wrapper(
                pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(
                        10 + index * 60, 10 + (index // 6) * 80, 50, 20
                    ),
                    text=f"{entity.name}",
                    manager=self.gui_manager,
                    container=entity_hover_data_panel_object,
                    object_id=pygame_gui.core.ObjectID(
                        class_id="ShowEntityButton",
                        object_id=entity_button_id,
                    ),
                ),
                entity_button_id,
                self.camera,
            )
            new_element_wrappers.append(entity_button_wrapper)
            self.temp_saved_buttons.append(entity_button_id)
        self.setup_elements(new_element_wrappers)

    def update_tile_info(self, tile: Tile) -> None:
        tile_hover_data_panel = self._element_manager.get_element(
            "tile_hover_data_panel"
        )
        tile_hover_data_panel_object = tile_hover_data_panel.get_interactable(
            pygame_gui.elements.UIPanel
        )
        new_element_wrappers = []
        coord_button_id = f"odd_r_coord_btn_{id(tile.coord)}"
        coord_button_wrapper = ui_element_wrapper(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(0, 0, 100, 20),
                text=f"Odd-R: {tile.coord}",
                manager=self.gui_manager,
                container=tile_hover_data_panel_object,
                object_id=pygame_gui.core.ObjectID(
                    class_id="OddRCoordButton",
                    object_id="odd_r_coord_button",
                ),
            ),
            registered_name=coord_button_id,
            camera=self.camera,
        )
        self.temp_saved_buttons.append(coord_button_id)
        new_element_wrappers.append(coord_button_wrapper)

        for index, feature in enumerate(tile.features):
            feature_button_id = f"feature_btn_{id(feature)}"
            feature_name, feature_description = feature.get_name_and_description()
            feature_button_wrapper = ui_element_wrapper(
                pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(100 + index * 60, (index // 6), 50, 20),
                    text=f"{feature_name}: {feature_description}",  # TODO: add place for description
                    manager=self.gui_manager,
                    container=tile_hover_data_panel_object,
                    object_id=pygame_gui.core.ObjectID(
                        class_id="feature_btn",
                        object_id=feature_button_id,
                    ),
                ),
                feature_button_id,
                self.camera,
            )
            # Store feature data in dictionary instead of attaching to button
            self.button_feature_data[feature_button_id] = feature
            new_element_wrappers.append(feature_button_wrapper)
            self.temp_saved_buttons.append(feature_button_id)
        self.setup_elements(new_element_wrappers)

    def kill_old_tile_data(self) -> None:
        for ids in self.temp_saved_buttons:
            self._element_manager.remove_element(ids)
            self.button_feature_data.pop(ids, None)  # Clean up feature data
        self.temp_saved_buttons.clear()

    def _refresh_move_history_panel(self) -> None:
        """Refresh the move history panel with current move history data."""
        try:
            move_history_panel = self._element_manager.get_element("move_history_panel")
        except KeyError:
            return

        move_history_panel_object = move_history_panel.get_interactable(
            pygame_gui.elements.UIPanel
        )

        for button_id in self.move_history_buttons:
            try:
                self._element_manager.remove_element(button_id)
            except KeyError:
                pass
            self.button_move_data.pop(button_id, None)
        self.move_history_buttons.clear()

        y_offset = 0
        displayed_moves = self.move_history[-10:]

        for index, move in enumerate(displayed_moves):
            button_id = f"move_history_btn_{id(move)}"
            is_player_turn = move["side"] == self.player_side
            turn_prefix = "[YOU]" if is_player_turn else "[ENEMY]"
            move_text = f"{turn_prefix} T{move['turn']}: {move['entity_name']}"

            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(0, y_offset, 195, 25),
                text=move_text,
                manager=self.gui_manager,
                container=move_history_panel_object,
                object_id=pygame_gui.core.ObjectID(
                    class_id="move_history_btn",
                    object_id=button_id,
                ),
            )
            self.button_move_data[button_id] = move
            self.move_history_buttons.append(button_id)
            y_offset += 25

    @input_event_bind("ShowEntityButton", pygame_gui.UI_BUTTON_PRESSED)
    def entity_selected(self, msg: pygame.event.Event) -> None:
        id = get_id(msg)
        assert id
        # The id is given as "entity_hover_data_panel.ShowEntityButton_x"
        entity_index = int(id.split("_")[-1])

        assert self.temp_selected_tile
        entity = self.temp_selected_tile.entities[entity_index]

        self.post(PageNavigationEvent([(PageNavigation.OPEN, "InspectEntity")]))
        self.post(PageCallbackEvent("crumb", payload=CrumbUpdatePayload(self.crumbs)))
        self.post(PageCallbackEvent("entity_data", payload=EntityPayload(entity)))

    # endregion
