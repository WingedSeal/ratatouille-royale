from typing import Final
from ratroyale.backend.hexagon import OddRCoord
from ratroyale.backend.crumbs_per_turn_modifier import CrumbsPerTurnModifier
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.payloads import (
    MoveHistoryPayload,
    FeaturePayload,
    SidePayload,
    TurnPayload,
)

from ratroyale.event_tokens.input_token import get_id
from ratroyale.frontend.visual.screen_constants import SCREEN_SIZE
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
from dataclasses import dataclass


@dataclass
class MoveEntry:
    entity_name: str
    from_pos: OddRCoord
    to_pos: OddRCoord
    turn: int
    side: Side


@register_page
class GameInfoPage(Page):
    def __init__(
        self, coordination_manager: CoordinationManager, camera: Camera
    ) -> None:
        self.crumbs = 0
        self.temp_saved_buttons: list[str] = []
        self.temp_selected_tile: Tile | None = None
        self.temp_hovered_tile: Tile | None = None
        self.crumbs_modifier: CrumbsPerTurnModifier | None = None
        self.move_history: list[MoveEntry] = []
        self.current_turn: int = 1
        self.current_turn_side: Side | None = None
        self.player_1_side: Side | None = None
        self.move_history_buttons: list[str] = []
        self.button_move_data: dict[str, MoveEntry] = {}
        self.button_feature_data: dict[str, Feature] = {}
        self.end_turn_button: pygame_gui.elements.UIButton | None = None
        # self.font = self.gui_manager.get_theme().get_font_dictionary().get_default_font()
        super().__init__(coordination_manager, camera, is_blocking=False)

    def define_initial_gui(self) -> list[ElementWrapper]:
        """Return all GUI elements for the TestPage."""
        gui_elements: list[ElementWrapper] = []

        # region Perm buttons/panels
        view_deck_button_pos = (0, SCREEN_SIZE[1] * 9 / 12)
        view_deck_button_dim = (SCREEN_SIZE[0] / 8, SCREEN_SIZE[1] / 12)
        view_deck_button_id = "view_deck_button"
        view_deck_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                view_deck_button_pos[0],
                view_deck_button_pos[1],
                view_deck_button_dim[0],
                view_deck_button_dim[1],
            ),
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
        show_crumbs_button_pos = (0, 0)
        show_crumbs_button_dim = (SCREEN_SIZE[0] / 8, SCREEN_SIZE[1] / 12)
        show_crumbs_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                show_crumbs_button_pos[0],
                show_crumbs_button_pos[1],
                show_crumbs_button_dim[0],
                show_crumbs_button_dim[1],
            ),
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
        end_turn_button_pos = (SCREEN_SIZE[0] * 7 / 8, SCREEN_SIZE[1] * 9 / 12)
        end_turn_button_dim = (SCREEN_SIZE[0] / 8, SCREEN_SIZE[1] / 12)
        self.end_turn_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                end_turn_button_pos[0],
                end_turn_button_pos[1],
                end_turn_button_dim[0],
                end_turn_button_dim[1],
            ),
            text="End Turn",
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="EndTurnButton",
                object_id="end_turn",
            ),
        )
        end_turn_button_element = ui_element_wrapper(
            self.end_turn_button, end_turn_button_id, self.camera
        )
        gui_elements.append(end_turn_button_element)
        # end region

        # region Panels visible on hover
        tile_hover_data_panel_id = "tile_hover_data_panel"
        tile_hover_data_panel_pos = (SCREEN_SIZE[0] * 2 / 8, 0)
        tile_hover_data_panel_dim = (SCREEN_SIZE[0] * 4 / 8, SCREEN_SIZE[1] / 12)
        tile_hover_data_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(
                tile_hover_data_panel_pos[0],
                tile_hover_data_panel_pos[1],
                tile_hover_data_panel_dim[0],
                tile_hover_data_panel_dim[1],
            ),
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
        entity_hover_data_panel_pos = (SCREEN_SIZE[0] * 2 / 8, SCREEN_SIZE[1] * 11 / 12)
        entity_hover_data_panel_dim = (SCREEN_SIZE[0] * 4 / 8, SCREEN_SIZE[1] / 12)
        entity_hover_data_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(
                entity_hover_data_panel_pos[0],
                entity_hover_data_panel_pos[1],
                entity_hover_data_panel_dim[0],
                entity_hover_data_panel_dim[1],
            ),
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
        move_history_panel_pos = (SCREEN_SIZE[0] * 6 / 8, SCREEN_SIZE[1] * 1 / 6)
        move_history_panel_dim = (SCREEN_SIZE[0] * 2 / 8, SCREEN_SIZE[1] * 1 / 2)
        move_history_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(
                move_history_panel_pos[0],
                move_history_panel_pos[1],
                move_history_panel_dim[0],
                move_history_panel_dim[1],
            ),
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
            self.current_turn_side = payload.player_1_side
            self.crumbs_modifier = payload.crumbs_modifier
        assert self.current_turn_side is not None
        end_turn_button = self._element_manager.get_element("end_turn_button")
        end_turn_button.get_interactable(pygame_gui.elements.UIButton).set_text(
            f"End Turn <{self.current_turn_side.to_string()}> ({self.current_turn})"
        )

    @callback_event_bind("tile_selected")
    def tile_selected(self, msg: PageCallbackEvent) -> None:
        if msg.success and msg.payload:
            payload = msg.payload
            assert isinstance(payload, TilePayload)
            if self.temp_selected_tile == payload.tile:
                self.temp_selected_tile = None
                self.kill_old_tile_data()
                return

            self.temp_selected_tile = payload.tile

            self.kill_old_tile_data()
            self.update_entity_info(self.temp_selected_tile)
            self.update_tile_info(self.temp_selected_tile)
            top_entity = (
                self.temp_selected_tile.entities[-1]
                if len(self.temp_selected_tile.entities) > 0
                else None
            )
            if top_entity:
                self.post(
                    PageNavigationEvent(
                        action_list=[
                            (PageNavigation.OPEN, "InspectEntity"),
                        ]
                    )
                )
                self.post(
                    PageCallbackEvent("crumb", payload=CrumbUpdatePayload(self.crumbs))
                )
                self.post(
                    PageCallbackEvent(
                        "entity_data",
                        payload=EntityPayload(top_entity),
                    )
                )

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
        try:
            assert self.player_side is not None
            side_payload = SidePayload(side=self.player_side)
            self.post(
                GameManagerEvent(
                    game_action="inspect_deck_clicked", payload=side_payload
                )
            )
        except Exception:
            pass

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
        assert event.entity.side is not None
        move_entry: MoveEntry = MoveEntry(
            event.entity.name,
            event.from_pos,
            event.path[-1],
            self.current_turn,
            event.entity.side,
        )
        self.move_history.append(move_entry)
        self._refresh_move_history_panel()

    @game_event_bind(EndTurnEvent)
    def on_end_turn(self, event: EndTurnEvent) -> None:
        """Track turn changes."""
        self.current_turn_side = event.to_side
        self.current_turn = event.turn_count
        self._refresh_move_history_panel()
        end_turn_button = self._element_manager.get_element("end_turn_button")
        end_turn_button.get_interactable(pygame_gui.elements.UIButton).set_text(
            f"End Turn <{self.current_turn_side.to_string()}> ({self.current_turn})"
        )

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
            turn_value = move_data.turn
            assert isinstance(turn_value, int), "turn must be an int"
            payload = MoveHistoryPayload(
                entity_name=move_data.entity_name,
                from_pos=move_data.from_pos,
                to_pos=move_data.to_pos,
                turn=turn_value,
                side=move_data.side,
                # is_player_1_move=(move_data["side"] == self.player_1_side),
            )
            self.post(PageNavigationEvent([(PageNavigation.OPEN, "InspectHistory")]))
            self.post(PageCallbackEvent("move_history_data", payload=payload))

    @input_event_bind("show_crumbs", pygame_gui.UI_BUTTON_PRESSED)
    def on_show_crumbs_button_click(self, msg: pygame.event.Event) -> None:
        assert self.current_turn_side is not None
        assert self.crumbs_modifier is not None
        payload = TurnPayload(
            self.current_turn,
            self.current_turn,
            self.current_turn_side,
            self.crumbs_modifier,
        )
        self.post(
            PageNavigationEvent(
                [
                    (PageNavigation.OPEN, "InspectCrumb"),
                ]
            )
        )
        self.post(PageCallbackEvent("show_crumbs", payload=payload))

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
        font = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, 0, 0),
            text="",
            manager=self.gui_manager,
            container=entity_hover_data_panel_object,
            object_id=pygame_gui.core.ObjectID(
                class_id="ShowEntityButton",
                object_id="__temp__",
            ),
        ).font
        assert font is not None
        PADDING_X: Final = 20
        PADDING_Y: Final = 10
        MARGIN: Final = 10
        new_element_wrappers: list[ElementWrapper] = []

        for index, entity in enumerate(reversed(tile.entities)):
            entity_button_id = f"ShowEntityButton_{index}"
            text_width, text_height = font.size(f"{entity.name}")
            entity_button_wrapper = ui_element_wrapper(
                pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(
                        (1 if index == 0 else 2) * MARGIN
                        + index * (text_width + PADDING_X),
                        10 + (index // 6) * (text_height + PADDING_Y),
                        text_width + PADDING_X,
                        text_height + PADDING_Y,
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
        font = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, 0, 0),
            text="",
            manager=self.gui_manager,
            container=tile_hover_data_panel_object,
            object_id=pygame_gui.core.ObjectID(
                class_id="ShowEntityButton",
                object_id="__temp__",
            ),
        ).font
        assert font is not None

        PADDING_X: Final = 10
        PADDING_Y: Final = 10
        MARGIN: Final = 10

        new_element_wrappers: list[ElementWrapper] = []
        coord_button_id = f"odd_r_coord_btn_{id(tile.coord)}"
        coord_button_wrapper = ui_element_wrapper(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(
                    PADDING_X, PADDING_Y, 120 + PADDING_X, 20 + PADDING_Y
                ),
                text=f"{tile.coord} Height: {tile.height}",
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
            text_width, text_height = font.size(feature_name)
            feature_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(
                    120
                    + (1 if index == 0 else 2) * MARGIN
                    + index * (text_width + PADDING_X),
                    10 + (index // 6) * (text_height + PADDING_Y),
                    text_width + PADDING_X,
                    text_height + PADDING_Y,
                ),
                text=f"{feature_name}",
                manager=self.gui_manager,
                container=tile_hover_data_panel_object,
                object_id=pygame_gui.core.ObjectID(
                    class_id="feature_btn",
                    object_id=feature_button_id,
                ),
            )
            # Attach feature data to button
            feature_button.feature_data = feature  # type: ignore

            feature_button_wrapper = ui_element_wrapper(
                feature_button,
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

    @callback_event_bind("player_1_info")
    def receive_player_1(self, msg: PageCallbackEvent) -> None:
        if msg.success and msg.payload:
            payload = msg.payload
            assert isinstance(payload, SidePayload)
            self.player_side = payload.side

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

        self.post(GameManagerEvent(game_action="get_player_1", payload=None))
        for index, move in enumerate(displayed_moves):
            button_id = f"move_history_btn_{id(move)}"
            is_player_1_turn = move.side == self.player_1_side
            turn_prefix = "[Player1]" if is_player_1_turn else "[Player2]"
            move_text = f"{turn_prefix} T{move.turn}: {move.entity_name}"

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
