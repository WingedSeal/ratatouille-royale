import pygame
import pygame_gui

from ratroyale.backend.board import Board
from ratroyale.backend.entity import Entity
from ratroyale.backend.tile import Tile
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.input_token import get_gesture_data, get_id, get_payload
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.visual_token import *
from ratroyale.frontend.gesture.gesture_data import GestureType

from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.event_binder import (
    input_event_bind,
    callback_event_bind,
)
from ratroyale.frontend.pages.page_managers.page_registry import register_page

from ratroyale.frontend.pages.page_elements.hitbox import RectangleHitbox, HexHitbox


from ratroyale.frontend.pages.page_elements.element import ElementWrapper, ElementParent


from ratroyale.frontend.visual.asset_management.sprite_key_registry import (
    TYPICAL_TILE_SIZE,
)

from ratroyale.frontend.pages.page_elements.spatial_component import (
    SpatialComponent,
    Camera,
)
from ratroyale.frontend.visual.asset_management.spritesheet_manager import (
    SpritesheetManager,
)
from ratroyale.frontend.visual.asset_management.game_obj_to_sprite_registry import (
    SPRITE_METADATA_REGISTRY,
    SQUEAK_IMAGE_METADATA_REGISTRY,
)
from ratroyale.backend.entities.rodents.vanguard import TailBlazer


from ratroyale.event_tokens.payloads import TilePayload, EntityPayload

from ratroyale.frontend.visual.asset_management.visual_component import VisualComponent
from ratroyale.frontend.visual.asset_management.spritesheet_structure import (
    SpritesheetComponent,
)
from ratroyale.frontend.visual.anim.presets.presets import (
    on_select_color_fade_in,
    on_select_color_fade_out,
    shrink_squeak,
    return_squeak_to_normal,
    default_idle_for_entity,
)

# Load a font, size 48, italic
italic_bold_arial = pygame.font.SysFont("Arial", 48, bold=True, italic=True)


# TODO: lots of refactorable spaghetti code
@register_page
class GameBoard(Page):
    def __init__(
        self, coordination_manager: CoordinationManager, camera: Camera
    ) -> None:
        super().__init__(coordination_manager, camera)
        self.selected_element_id: tuple[str, str] | None = None
        self.hovered_tile_id: tuple[str, str] | None = None
        self.dragging_element_id: tuple[str, str] | None = None

        self.ability_panel_id: str | None = None

        self.selected_squeak: str | None = None

    def on_open(self) -> None:
        self.post(GameManagerEvent(game_action="start_game"))

    def define_initial_gui(self) -> list[ElementWrapper]:
        return []

    # region Input Bindings

    @callback_event_bind("start_game")
    def _start_game(self, msg: PageCallbackEvent[Board]) -> None:
        """Handle the response from starting a game."""

        if msg.success and msg.payload:
            self.board = msg.payload
            element_configs: list[ElementWrapper] = []
            tiles = self.board.tiles
            entities = self.board.cache.entities

            for tile_list in tiles:
                for tile in tile_list:
                    if tile:
                        sprite_metadata = SPRITE_METADATA_REGISTRY[TailBlazer]
                        cached_spritesheet_name = (
                            SpritesheetManager.register_spritesheet(
                                sprite_metadata
                            ).get_key()
                        )

                        tile_element = ElementWrapper(
                            registered_name=f"tile_{id(tile)}",
                            grouping_name="TILE",
                            camera=self.camera,
                            spatial_component=SpatialComponent(
                                pygame.Rect(self._define_tile_rect(tile)),
                                space_mode="WORLD",
                            ),
                            interactable_component=HexHitbox(),
                            visual_component=VisualComponent(
                                SpritesheetComponent(
                                    spritesheet_reference=cached_spritesheet_name
                                ),
                                "IDLE",
                            ),
                            payload=TilePayload(tile),
                        )
                        element_configs.append(tile_element)

            for entity in entities:
                spritesheet_component = SpritesheetComponent(cached_spritesheet_name)
                visual_component = VisualComponent(spritesheet_component, "IDLE")
                visual_component.set_default_animation(
                    default_idle_for_entity(spritesheet_component)
                )
                entity_element = ElementWrapper(
                    registered_name=f"entity_{id(tile)}",
                    grouping_name="ENTITY",
                    camera=self.camera,
                    spatial_component=SpatialComponent(
                        pygame.Rect(self._define_entity_rect(entity)),
                        space_mode="WORLD",
                        z_order=1,
                    ),
                    interactable_component=RectangleHitbox(),
                    visual_component=visual_component,
                    payload=EntityPayload(entity),
                )

                element_configs.append(entity_element)

            SQUEAK_WIDTH, SQUEAK_HEIGHT = 143, 90
            SQUEAK_SPACING = 10
            LEFT_MARGIN = 0
            TOP_MARGIN = 80

            sprite_metadata = SQUEAK_IMAGE_METADATA_REGISTRY[TailBlazer]
            cached_spritesheet_name = SpritesheetManager.register_spritesheet(
                sprite_metadata
            ).get_key()

            for i in range(5):
                # Base card rect
                squeak_rect = pygame.Rect(
                    LEFT_MARGIN,
                    TOP_MARGIN + i * (SQUEAK_HEIGHT + SQUEAK_SPACING),
                    SQUEAK_WIDTH,
                    SQUEAK_HEIGHT,
                )

                # Create card element
                squeak_element = ElementWrapper(
                    registered_name=f"squeak_{i}",
                    grouping_name="SQUEAK",
                    camera=self.camera,
                    spatial_component=SpatialComponent(
                        squeak_rect, space_mode="SCREEN", z_order=100
                    ),
                    interactable_component=RectangleHitbox(),
                    is_blocking=False,
                    visual_component=VisualComponent(
                        SpritesheetComponent(
                            spritesheet_reference=cached_spritesheet_name
                        ),
                        "NONE",
                    ),
                )

                # Render cost text
                squeak_cost_text = italic_bold_arial.render(
                    "100", False, pygame.Color(255, 255, 255)
                )
                # Compute cost rect anchored to bottom-right of card
                cost_width, cost_height = squeak_cost_text.get_size()
                PADDING = 5

                # --- Local position relative to the card (bottom-right corner) ---
                cost_rect = pygame.Rect(
                    squeak_rect.right - cost_width - PADDING,
                    squeak_rect.bottom - squeak_rect.height,
                    cost_width,
                    cost_height,
                )

                # Create cost element
                squeak_cost_element = ElementWrapper(
                    registered_name=f"squeakCost_{i}",
                    grouping_name="SQUEAKCOST",
                    camera=self.camera,
                    spatial_component=SpatialComponent(
                        cost_rect, space_mode="SCREEN", z_order=101
                    ),
                    interactable_component=None,
                    is_blocking=False,
                    visual_component=VisualComponent(
                        SpritesheetComponent(spritesheet_reference=squeak_cost_text),
                        "NONE",
                    ),
                    element_parent=ElementParent(f"squeak_{i}", "SQUEAK"),
                )

                element_configs.append(squeak_element)
                element_configs.append(squeak_cost_element)

            self.setup_elements(element_configs)
        else:
            raise RuntimeError(f"Failed to start game: {msg.error_msg}")

    # region Tile Related Events

    @input_event_bind("tile", GestureType.CLICK.to_pygame_event())
    def _on_tile_click(self, msg: pygame.event.Event) -> None:
        tile_element_id = self._get_element_id(msg)

        self._select_element("TILE", tile_element_id, toggle=True)
        self._close_ability_menu()

    # endregion

    # region Entity Related Events

    @input_event_bind("entity", GestureType.CLICK.to_pygame_event())
    def _on_entity_click(self, msg: pygame.event.Event) -> None:
        entity_element_id = self._get_element_id(msg)

        self._select_element("ENTITY", entity_element_id)
        self._close_ability_menu()

    @input_event_bind("entity", GestureType.HOLD.to_pygame_event())
    def _display_ability_menu(self, msg: pygame.event.Event) -> None:
        """Display the ability menu for the selected entity."""
        entity_payload = get_payload(msg)
        entity_element_id = get_id(msg)
        if not entity_payload or not entity_element_id:
            raise ValueError(
                "Wrong event type received. Make sure it is a gesture type event!"
            )

        entity_element = self._element_manager.get_element_wrapper(
            entity_element_id, "ENTITY"
        )
        if not entity_element:
            raise ValueError("Something went wrong while trying to get the element.")

        assert isinstance(entity_payload, EntityPayload)
        entity = entity_payload.entity
        # region Create ability panel
        # --- Create a parent panel for all ability buttons ---
        entity_spatial_rect = entity_element.spatial_component.get_screen_rect(
            self.camera
        )
        entity_center_x = entity_spatial_rect.x + entity_spatial_rect.width / 2
        entity_center_y = entity_spatial_rect.y + entity_spatial_rect.height / 2

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

        panel_element = ElementWrapper(
            registered_name=panel_id,
            grouping_name="UI_ELEMENT",
            camera=self.camera,
            spatial_component=SpatialComponent(panel_object.get_abs_rect()),
            interactable_component=panel_object,
            visual_component=VisualComponent(),
        )
        self.setup_elements([panel_element])

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

    # Called when drag starts; aligns the entity's center to the mouse
    @input_event_bind("entity", GestureType.DRAG_START.to_pygame_event())
    def _on_entity_drag_start(self, msg: pygame.event.Event) -> None:
        entity_element_id = self._get_element_id(msg)
        entity_element = self._element_manager.get_element_wrapper(
            entity_element_id, "ENTITY"
        )
        gesture_data = get_gesture_data(msg)

        if entity_element and gesture_data.mouse_pos and entity_element_id:
            entity_element.spatial_component.center_to_screen_pos(
                gesture_data.mouse_pos, self.camera
            )
            self.dragging_element_id = (entity_element_id, "ENTITY")

    # endregion

    # region Squeak Related Events

    @input_event_bind("squeak", GestureType.CLICK.to_pygame_event())
    def squeak_clicked(self, msg: pygame.event.Event) -> None:
        squeak_id = get_id(msg)
        if squeak_id:
            self.selected_squeak = squeak_id

    @input_event_bind("squeak", GestureType.DRAG_START.to_pygame_event())
    def squeak_drag_start(self, msg: pygame.event.Event) -> None:
        squeak_id = get_id(msg)
        gesture_data = get_gesture_data(msg)
        if squeak_id:
            squeak_element = self._element_manager.get_element_wrapper(
                squeak_id, "SQUEAK"
            )

        if squeak_element and gesture_data.mouse_pos and squeak_id:
            squeak_element.spatial_component.center_to_screen_pos(
                gesture_data.mouse_pos, self.camera
            )
            self.dragging_element_id = (squeak_id, "SQUEAK")
            vis = squeak_element.visual_component
            spatial = squeak_element.spatial_component
            if vis and vis.spritesheet_component:
                vis.queue_override_animation(shrink_squeak(spatial, self.camera))

    # endregion

    # region Dragging logic

    # Called while dragging; moves element regardless of hitbox
    @input_event_bind(None, GestureType.DRAG.to_pygame_event())
    def _on_drag(self, msg: pygame.event.Event) -> None:
        if self.dragging_element_id is None:
            self.camera.drag_to(pygame.mouse.get_pos())
            return

        category, element_id = self.dragging_element_id
        entity = self._element_manager.get_element_wrapper(category, element_id)
        gesture_data = get_gesture_data(msg)

        if entity and gesture_data.mouse_pos:
            entity.spatial_component.center_to_screen_pos(
                gesture_data.mouse_pos, self.camera
            )

        if element_id and element_id.split("_")[0] == "tile":
            self._update_tile_hover(element_id)
        else:
            # If no tile under mouse, remove previous highlight
            if self.hovered_tile_id:
                prev_id, prev_type = self.hovered_tile_id
                prev_tile = self.get_element(prev_id, prev_type)
                if prev_tile and prev_tile.visual_component:
                    vis = prev_tile.visual_component
                    if vis and vis.spritesheet_component:
                        vis.queue_override_animation(
                            on_select_color_fade_out(
                                vis.spritesheet_component,
                                color=pygame.Color(255, 255, 255),
                            )
                        )
                self.hovered_tile_id = None

    @input_event_bind(None, GestureType.DRAG_END.to_pygame_event())
    def _on_drag_end(self, msg: pygame.event.Event) -> None:
        self.dragging_element_id = None
        self.camera.end_drag()

    @input_event_bind("squeak", GestureType.DRAG_END.to_pygame_event())
    def squeak_drag_end(self, msg: pygame.event.Event) -> None:
        squeak_id = get_id(msg)
        if squeak_id:
            squeak_elem = self.get_element(squeak_id, "SQUEAK")
            if squeak_elem and squeak_elem.visual_component:
                vis = squeak_elem.visual_component
                if vis and vis.spritesheet_component:
                    spatial = squeak_elem.spatial_component
                    vis.queue_override_animation(
                        return_squeak_to_normal(spatial, self.camera)
                    )

    # endregion

    # region Camera Zooming Logic

    @input_event_bind(None, pygame.MOUSEWHEEL)
    def _on_scroll(self, msg: pygame.event.Event) -> None:
        if msg.y == 1:
            self.camera.zoom_at(self.camera.scale + 0.1, pygame.mouse.get_pos())
        elif msg.y == -1:
            self.camera.zoom_at(self.camera.scale - 0.1, pygame.mouse.get_pos())

    # endregion

    # endregion

    # region Utilities

    def _close_ability_menu(self) -> None:
        """Close the ability menu if open."""
        if self.ability_panel_id:
            self._element_manager.remove_element("UI_ELEMENT", self.ability_panel_id)
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
    ) -> ElementWrapper | None:
        """
        Handles single-selection logic for both tiles and entities.
        Only one element can be selected at a time.

        Returns the currently selected element, or None if deselected.
        """
        # Un-highlight previous selection
        prev_element: ElementWrapper | None = None
        if self.selected_element_id:
            prev_type, prev_id = self.selected_element_id
            prev_element = self.get_element(prev_type, prev_id)
            if prev_element and prev_element.visual_component:
                vis = prev_element.visual_component
                if vis and vis.spritesheet_component:
                    vis.queue_override_animation(
                        on_select_color_fade_out(
                            vis.spritesheet_component, color=pygame.Color(255, 255, 255)
                        )
                    )

        # Deselect if same element clicked
        if self.selected_element_id == (element_id, element_type) and toggle:
            self.selected_element_id = None
            return None

        # Highlight new element
        element = self.get_element(element_id, element_type)
        if element and element.visual_component:
            vis = element.visual_component
            if vis and vis.spritesheet_component:
                vis.queue_override_animation(
                    on_select_color_fade_in(
                        vis.spritesheet_component, color=pygame.Color(255, 255, 255)
                    )
                )

        # Update selection
        self.selected_element_id = (element_id, element_type)

        return element

    def _update_tile_hover(self, tile_id: str) -> None:
        """
        Called whenever a card is being dragged. Highlights the tile under the card.
        """
        # If the hovered tile hasn't changed, do nothing
        if self.hovered_tile_id and self.hovered_tile_id[0] == tile_id:
            return

        # Un-highlight previous tile
        if self.hovered_tile_id:
            prev_id, prev_type = self.hovered_tile_id
            prev_tile = self.get_element(prev_id, prev_type)
            if prev_tile and prev_tile.visual_component:
                vis = prev_tile.visual_component
                if vis and vis.spritesheet_component:
                    vis.queue_override_animation(
                        on_select_color_fade_out(
                            vis.spritesheet_component, color=pygame.Color(255, 255, 255)
                        )
                    )

        # Highlight new tile
        tile = self.get_element(tile_id, "TILE")
        if tile and tile.visual_component:
            vis = tile.visual_component
            if vis and vis.spritesheet_component:
                vis.queue_override_animation(
                    on_select_color_fade_in(
                        vis.spritesheet_component, color=pygame.Color(255, 255, 255)
                    )
                )

        self.hovered_tile_id = (tile_id, "TILE")

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
