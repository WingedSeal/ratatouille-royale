from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.input_token import (
    get_id,
    get_gesture_data,
    get_payload,
)
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *

from ratroyale.frontend.gesture.gesture_data import GestureType

from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.event_binder import (
    input_event_bind,
    callback_event_bind,
)
from ratroyale.frontend.pages.page_managers.page_registry import register_page
from ratroyale.frontend.pages.page_managers.backend_adapter import (
    get_name_from_entity,
    get_name_from_tile,
)

from ratroyale.frontend.pages.page_elements.element_builder import (
    ElementConfig,
    UIRegisterForm,
)
from ratroyale.frontend.pages.page_elements.element import Element

from ratroyale.backend.board import Board
from ratroyale.backend.tile import Tile
from ratroyale.backend.entity import Entity

from ratroyale.frontend.visual.asset_management.sprite_registry import TYPICAL_TILE_SIZE

import pygame_gui
import pygame

from typing import Any


@register_page
class GameBoard(Page):
    def __init__(self, coordination_manager: CoordinationManager) -> None:
        super().__init__(coordination_manager)
        self.selected_element_id: tuple[str, str] | None = None
        self.ability_panel_id: str | None = None
        self.board: Board | None = None
        self.dragging_element_id: tuple[str, str] | None = None

    def on_open(self) -> None:
        self.post(GameManagerEvent(game_action="start_game"))

    def define_initial_gui(self) -> list[UIRegisterForm]:
        return []

    # region Input Bindings

    @callback_event_bind("start_game")
    def _start_game(self, msg: PageCallbackEvent[Board]) -> None:
        """Handle the response from starting a game."""

        if msg.success and msg.payload:
            self.board = msg.payload
            element_configs: list[ElementConfig[Any]] = []
            tiles = self.board.tiles
            entities = self.board.cache.entities

            for tile_list in tiles:
                for tile in tile_list:
                    if tile:
                        tile_element = ElementConfig[Tile](
                            element_type="tile",
                            id=get_name_from_tile(tile),
                            rect=self._define_tile_rect(tile),
                            payload=tile,
                        )
                        element_configs.append(tile_element)

            for entity in entities:
                entity_element = ElementConfig[Entity](
                    element_type="entity",
                    id=get_name_from_entity(entity),
                    rect=self._define_entity_rect(entity),
                    payload=entity,
                    z_order=1,  # Ensure entities are rendered above tiles
                )
                element_configs.append(entity_element)

            self.setup_elements(element_configs)
        else:
            raise RuntimeError(f"Failed to start game: {msg.error_msg}")

    # TODO: fire normal clicks with double click.
    @input_event_bind("tile", GestureType.CLICK.to_pygame_event())
    def _on_tile_click(self, msg: pygame.event.Event) -> None:
        tile_element_id = self._get_element_id(msg)

        self._select_element("tile", tile_element_id)
        self._close_ability_menu()

    @input_event_bind("entity", GestureType.CLICK.to_pygame_event())
    def _on_entity_click(self, msg: pygame.event.Event) -> None:
        entity_element_id = self._get_element_id(msg)

        self._select_element("entity", entity_element_id)
        self._close_ability_menu()

    @input_event_bind("tile", GestureType.HOVER.to_pygame_event())
    def _on_tile_hover(self, msg: pygame.event.Event) -> None:
        tile_element_id = self._get_element_id(msg)

        curr_tile = self._select_element("tile", tile_element_id)
        self.post(
            GameManagerEvent(
                game_action="tile_hover",
                payload=curr_tile if curr_tile else None,
            )
        )

    @input_event_bind("entity", GestureType.HOLD.to_pygame_event())
    def _display_ability_menu(self, msg: pygame.event.Event) -> None:
        """Display the ability menu for the selected entity."""
        entity = get_payload(msg)
        entity_element_id = get_id(msg)
        if not entity or not entity_element_id:
            raise ValueError(
                "Wrong event type received. Make sure it is a gesture type event!"
            )

        entity_element = self._element_manager.get_element("entity", entity_element_id)
        if not entity_element:
            raise ValueError("Something went wrong while trying to get the element.")

        assert isinstance(entity, Entity)
        # region Create ability panel
        # --- Create a parent panel for all ability buttons ---
        entity_center_x = (
            entity_element.get_topleft()[0] + entity_element.get_size()[0] / 2
        )
        entity_center_y = (
            entity_element.get_topleft()[1] + entity_element.get_size()[1] / 2
        )

        panel_width = 160
        panel_x = entity_center_x - panel_width / 2
        panel_y = entity_center_y
        panel_id = "ability_panel"
        self.ability_panel_id = panel_id
        panel_rect = pygame.Rect(
            panel_x, panel_y, panel_width, len(entity.skills) * 30 + 10
        )
        panel_object = pygame_gui.elements.UIPanel(
            relative_rect=panel_rect,
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="AbilityPanel", object_id=panel_id
            ),
        )

        panel_element = UIRegisterForm(panel_id, panel_object)

        self.setup_gui_elements([panel_element])

        # --- Create ability buttons inside the panel ---
        for i, skill in enumerate(entity.skills):
            element_id = f"ability_{i}_from_{entity_element_id}"

            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(0, i * 30, 150, 30),
                text=skill.name,
                manager=self.gui_manager,
                container=panel_object,
                object_id=pygame_gui.core.ObjectID(
                    class_id="AbilityButton", object_id=element_id
                ),
            )
        # endregion

    @input_event_bind("ability", pygame_gui.UI_BUTTON_PRESSED)
    def _activate_ability(self, msg: pygame.event.Event) -> None:
        """Activate selected ability."""
        self._close_ability_menu()
        entity_element_id = get_id(msg)
        if not entity_element_id:
            raise ValueError(
                "Wrong event type received. Make sure it is a gesture type event!"
            )

        # self._select_element("entity", entity_element_id)

    # Called when drag starts; aligns the entity's center to the mouse
    @input_event_bind("entity", GestureType.DRAG_START.to_pygame_event())
    def _on_entity_drag_start(self, msg: pygame.event.Event) -> None:
        entity_element_id = self._get_element_id(msg)
        entity_element = self._element_manager.get_element("entity", entity_element_id)
        gesture_data = get_gesture_data(msg)

        if entity_element and gesture_data.mouse_pos and entity_element_id:
            mouse_x, mouse_y = gesture_data.mouse_pos
            width, height = entity_element.get_size()
            new_x = mouse_x - width // 2
            new_y = mouse_y - height // 2
            entity_element.set_position((new_x, new_y))
            self.dragging_element_id = ("entity", entity_element_id)

    # Called while dragging; moves element regardless of hitbox
    @input_event_bind(None, GestureType.DRAG.to_pygame_event())
    def _on_entity_drag(self, msg: pygame.event.Event) -> None:
        if self.dragging_element_id is None:
            return

        category, element_id = self.dragging_element_id
        entity = self._element_manager.get_element(category, element_id)
        gesture_data = get_gesture_data(msg)

        if entity and gesture_data.mouse_pos:
            width, height = entity.get_size()
            new_topleft = (
                gesture_data.mouse_pos[0] - width // 2,
                gesture_data.mouse_pos[1] - height // 2,
            )
            entity.set_position(new_topleft)

    @input_event_bind(None, GestureType.DRAG_END.to_pygame_event())
    def _on_drag_end(self, msg: pygame.event.Event) -> None:
        self.dragging_element_id = None

    # TODO: fix swipe (very inconsistent ATM)
    @input_event_bind(None, GestureType.SWIPE.to_pygame_event())
    def _on_swipe_test(self, msg: pygame.event.Event) -> None:
        print("Swipe test")

    @callback_event_bind("entity_list")
    def _print_test(self, msg: pygame.event.Event) -> None:
        print("Cross page listening")

    # endregion

    # region Utilities

    def _close_ability_menu(self) -> None:
        """Close the ability menu if open."""
        if self.ability_panel_id:
            self._element_manager.remove_gui_element(self.ability_panel_id)
            self.ability_panel_id = None

    def _get_element_id(self, msg: pygame.event.Event) -> str:
        element_id = get_id(msg)
        if not element_id:
            raise ValueError(
                "Wrong event type received. Make sure it is a gesture type event!"
            )
        return element_id

    def _select_element(
        self, element_type: str, element_id: str, toggle: bool = True
    ) -> Element[Tile | Entity] | None:
        """
        Handles single-selection logic for both tiles and entities.
        Only one element can be selected at a time.

        Returns the currently selected element, or None if deselected.
        """
        # Un-highlight previous selection
        prev_element: Element[Tile | Entity] | None = None
        if self.selected_element_id:
            prev_type, prev_id = self.selected_element_id
            prev_element = self.get_element(prev_type, prev_id)
            if prev_element and prev_element.visual:
                prev_element.visual.set_highlighted(False)

        # Deselect if same element clicked
        if self.selected_element_id == (element_type, element_id) and toggle:
            self.selected_element_id = None
            return None

        # Highlight new element
        element = self.get_element(element_type, element_id)
        if element and element.visual:
            element.visual.set_highlighted(True)

        # Update selection
        self.selected_element_id = (element_type, element_id)

        return element

    def _get_ability_id(self, msg: pygame.event.Event) -> int:
        ability_button_elem_id = self.get_leaf_object_id(self._get_element_id(msg))
        if ability_button_elem_id:
            return int(ability_button_elem_id.split("_")[1])
        else:
            raise ValueError("Ability button elem id is None.")

    # TODO: could be moved to elsewhere
    def _define_tile_rect(self, tile: Tile) -> tuple[float, float, float, float]:
        """Given a Tile, return its bounding rectangle as (x, y, width, height)."""
        pixel_x, pixel_y = tile.coord.to_pixel(*TYPICAL_TILE_SIZE, is_bounding_box=True)
        width, height = TYPICAL_TILE_SIZE
        return (pixel_x, pixel_y, width, height)

    def _define_entity_rect(self, entity: Entity) -> tuple[float, float, float, float]:
        """Given an Entity, return its bounding rectangle as (x, y, width, height)."""
        pixel_x, pixel_y = entity.pos.to_pixel(*TYPICAL_TILE_SIZE, is_bounding_box=True)
        width, height = (40, 40)  # Placeholder size for entity
        return (pixel_x, pixel_y, width, height)

    # endregion
