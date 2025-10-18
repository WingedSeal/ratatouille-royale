import pygame
import pygame_gui

from ratroyale.backend.entity import Entity
from ratroyale.backend.tile import Tile
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.input_token import get_gesture_data, get_id, get_payload
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.visual_token import *
from ratroyale.frontend.gesture.gesture_data import GestureType
from ratroyale.event_tokens.payloads import SqueakPlacementPayload, SqueakPayload

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
    TILE_SPRITE_METADATA,
)
from ratroyale.backend.entities.rodents.vanguard import TailBlazer
from ratroyale.backend.player_info.squeak import Squeak
from ratroyale.backend.hexagon import OddRCoord


from ratroyale.event_tokens.payloads import (
    TilePayload,
    EntityPayload,
    GameSetupPayload,
    CrumbUpdatePayload,
    SqueakPlacableTilesPayload,
)

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
from enum import Enum

# Load a font, size 48, italic
italic_bold_arial = pygame.font.SysFont("Arial", 48, bold=True, italic=True)


class SavedKey(Enum):
    SELECTED_TILE = "TILE"
    SELECTED_ENTITY = "ENTITY"
    SELECTED_SQUEAK = "SQUEAK"


SQUEAK_WIDTH, SQUEAK_HEIGHT = 112, 70
SQUEAK_SPACING = 5
LEFT_MARGIN = 0
TOP_MARGIN = 80

CARD_RECT = pygame.Rect(LEFT_MARGIN, TOP_MARGIN, SQUEAK_WIDTH, SQUEAK_HEIGHT)


@register_page
class GameBoard(Page):
    def __init__(
        self, coordination_manager: CoordinationManager, camera: Camera
    ) -> None:
        super().__init__(coordination_manager, camera)
        self.saved_element_ids: dict[SavedKey, str | None] = {
            SavedKey.SELECTED_TILE: None,
            SavedKey.SELECTED_ENTITY: None,
            SavedKey.SELECTED_SQUEAK: None,
        }

        self.squeak_in_hand: list[str] = []
        self.hand_slots_element: list[str] = []
        self.player_crumbs: int = 0

        self.ability_panel_id: str | None = None

    def on_open(self) -> None:
        self.post(GameManagerEvent(game_action="start_game"))

    def define_initial_gui(self) -> list[ElementWrapper]:
        return []

    # region Callbacks from Backend

    @callback_event_bind("start_game")
    def _start_game(self, msg: PageCallbackEvent) -> None:
        """Handle the response from starting a game."""

        if msg.success and msg.payload:
            assert isinstance(msg.payload, GameSetupPayload)
            board = msg.payload.board
            element_configs: list[ElementWrapper] = []
            tiles = board.tiles
            entities = board.cache.entities

            for tile_list in tiles:
                for tile in tile_list:
                    if tile:
                        tile_element = self.tile_element_creator(tile)
                        element_configs.append(tile_element)

            for entity in entities:
                entity_element = self.entity_element_creator(entity, entity.pos)
                element_configs.append(entity_element)

            squeak_list = msg.payload.hand_squeaks

            for i, squeak in enumerate(squeak_list):
                squeak_element, squeak_cost_element = self.squeak_element_creator(
                    squeak, i
                )

                card_rect = CARD_RECT.copy()
                card_rect.y += i * (SQUEAK_HEIGHT + SQUEAK_SPACING)

                slot_id = f"hand_slot_{i}"
                slot = ElementWrapper(
                    registered_name=slot_id,
                    grouping_name="HANDSLOT",
                    camera=self.camera,
                    spatial_component=SpatialComponent(
                        local_rect=card_rect,
                        z_order=99,
                    ),
                )
                self.hand_slots_element.append(slot_id)

                element_configs.append(squeak_element)
                element_configs.append(squeak_cost_element)
                element_configs.append(slot)

            self.setup_elements(element_configs)

            self.player_crumbs = msg.payload.starting_crumbs
        else:
            raise RuntimeError(f"Failed to start game: {msg.error_msg}")

    @callback_event_bind("crumb_update")
    def _crumb_update(self, msg: PageCallbackEvent) -> None:
        """Handle crumb update from backend."""
        if msg.success and msg.payload:
            assert isinstance(msg.payload, CrumbUpdatePayload)
            self.player_crumbs = msg.payload.new_crumb_amount

    @callback_event_bind("handle_squeak_placable_tiles")
    def _handle_squeak_placable_tiles(self, msg: PageCallbackEvent) -> None:
        """Handle squeak placable tiles from backend."""
        if msg.success and msg.payload:
            assert isinstance(msg.payload, SqueakPlacableTilesPayload)

    # endregion

    # region Tile Related Events

    @input_event_bind("tile", GestureType.CLICK.to_pygame_event())
    def _on_tile_click(self, msg: pygame.event.Event) -> None:
        id = get_id(msg)
        self._select_deselect_logic(SavedKey.SELECTED_TILE, id, True)

        self._close_ability_menu()

    # endregion

    # region Entity Related Events

    @input_event_bind("entity", GestureType.HOVER.to_pygame_event())
    def _entity_hover_test(self, msg: pygame.event.Event) -> None:
        """Test hover event on entity."""
        id = get_id(msg)
        duration = get_gesture_data(msg).duration if get_gesture_data(msg) else 0.0
        # For testing purposes, we just print the hover info
        print(f"Hovering over entity {id} for {duration:.2f} seconds.")

    @input_event_bind("entity", GestureType.CLICK.to_pygame_event())
    def _on_entity_click(self, msg: pygame.event.Event) -> None:
        id = get_id(msg)
        self._select_deselect_logic(SavedKey.SELECTED_ENTITY, id, True)
        self._close_ability_menu()

    @input_event_bind("entity", GestureType.HOLD.to_pygame_event())
    def _display_ability_menu(self, msg: pygame.event.Event) -> None:
        """Display the ability menu for the selected entity."""
        entity_payload = get_payload(msg)
        id = get_id(msg)
        if not entity_payload or not id:
            raise ValueError(
                "Wrong event type received. Make sure it is a gesture type event!"
            )

        self._select_deselect_logic(SavedKey.SELECTED_TILE, id, False)

        entity_element = self._element_manager.get_element_wrapper(
            id, SavedKey.SELECTED_ENTITY.value
        )

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
            element_id = f"ability_{i}"

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

    # endregion

    # region Squeak Related Events

    @input_event_bind("squeak", GestureType.CLICK.to_pygame_event())
    def squeak_clicked(self, msg: pygame.event.Event) -> None:
        id = get_id(msg)
        self._select_deselect_logic(SavedKey.SELECTED_SQUEAK, id, True)

    @input_event_bind("squeak", GestureType.DRAG_START.to_pygame_event())
    def squeak_drag_start(self, msg: pygame.event.Event) -> None:
        squeak_element_id = get_id(msg)
        gesture_data = get_gesture_data(msg)
        if squeak_element_id:
            squeak_element = self._element_manager.get_element_wrapper(
                squeak_element_id, "SQUEAK"
            )

        if squeak_element and gesture_data.mouse_pos and squeak_element_id:
            squeak_element.spatial_component.center_to_screen_pos(
                gesture_data.mouse_pos, self.camera
            )
            self.saved_element_ids[SavedKey.SELECTED_SQUEAK] = squeak_element_id
            vis = squeak_element.visual_component
            spatial = squeak_element.spatial_component
            if vis and vis.spritesheet_component:
                vis.queue_override_animation(shrink_squeak(spatial, self.camera))

        squeak = squeak_element.get_payload(SqueakPayload)
        self.coordination_manager.put_message(
            GameManagerEvent[SqueakPayload](
                game_action="get_squeak_placable_tiles", payload=squeak
            )
        )

    # endregion

    # region Dragging logic

    # Called while dragging; moves element regardless of hitbox
    @input_event_bind(None, GestureType.DRAG.to_pygame_event())
    def _on_drag(self, msg: pygame.event.Event) -> None:
        element_id = self.saved_element_ids[SavedKey.SELECTED_SQUEAK]
        if element_id is None:
            self.camera.drag_to(pygame.mouse.get_pos())
            return

        entity = self._element_manager.get_element_wrapper(
            element_id, SavedKey.SELECTED_SQUEAK.value
        )
        gesture_data = get_gesture_data(msg)

        if entity and gesture_data.mouse_pos:
            entity.spatial_component.center_to_screen_pos(
                gesture_data.mouse_pos, self.camera
            )

        tile_element_id = get_id(msg)
        self._select_deselect_logic(SavedKey.SELECTED_TILE, tile_element_id, False)

    @input_event_bind(None, GestureType.DRAG_END.to_pygame_event())
    def _on_drag_end(self, msg: pygame.event.Event) -> None:
        selected_squeak_id = self.saved_element_ids[SavedKey.SELECTED_SQUEAK]
        selected_tile_id = self.saved_element_ids[SavedKey.SELECTED_TILE]

        if selected_squeak_id and selected_tile_id:
            tile_element = self.get_element(selected_tile_id, "TILE")
            tile_payload: TilePayload = tile_element.get_payload(TilePayload)

            self.coordination_manager.put_message(
                GameManagerEvent[SqueakPlacementPayload](
                    game_action="squeak_tile_interaction",
                    payload=SqueakPlacementPayload(
                        hand_index=self.squeak_in_hand.index(selected_squeak_id),
                        tile_coord=tile_payload.tile.coord,
                    ),
                )
            )

        self._deselection(SavedKey.SELECTED_SQUEAK)
        self._deselection(SavedKey.SELECTED_TILE)

        # Remove squeak element and spawn a rodent

        self.camera.end_drag()

    @input_event_bind("squeak", GestureType.DRAG_END.to_pygame_event())
    def return_squeak_to_size_end_drag(self, msg: pygame.event.Event) -> None:
        squeak_id = get_id(msg)
        assert squeak_id

        squeak_hand_index = self.squeak_in_hand.index(squeak_id)
        hand_slot_id = self.hand_slots_element[squeak_hand_index]
        hand_slot_element = self.get_element(hand_slot_id, "HANDSLOT")
        hand_slot_topleft = hand_slot_element.spatial_component.get_screen_rect(
            self.camera
        ).topleft

        squeak_elem = self.get_element(squeak_id, "SQUEAK")
        spatial = squeak_elem.spatial_component
        squeak_elem.queue_override_animation(
            return_squeak_to_normal(
                spatial, self.camera, hand_slot_topleft, CARD_RECT.size
            )
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

    # region UTILITY METHODS

    def tile_element_creator(self, tile: Tile) -> ElementWrapper:
        # TODO: change the hardcoded tile number to tile sprite number
        sprite_metadata = TILE_SPRITE_METADATA[0]
        cached_spritesheet_name = SpritesheetManager.register_spritesheet(
            sprite_metadata
        ).get_key()

        tile_element = ElementWrapper(
            registered_name=f"tile_{id(tile)}",
            grouping_name="TILE",
            camera=self.camera,
            spatial_component=SpatialComponent(
                pygame.Rect(self._define_tile_rect(tile)), space_mode="WORLD"
            ),
            interactable_component=HexHitbox(),
            visual_component=VisualComponent(
                SpritesheetComponent(spritesheet_reference=cached_spritesheet_name),
                "NONE",
            ),
            payload=TilePayload(tile),
        )
        return tile_element

    def entity_element_creator(self, entity: Entity, pos: OddRCoord) -> ElementWrapper:
        # TODO: change the hardcoded type to entity type
        # TODO: when I place squeaks how do I know what entity to create?
        sprite_metadata = SPRITE_METADATA_REGISTRY[TailBlazer]
        cached_spritesheet_name = SpritesheetManager.register_spritesheet(
            sprite_metadata
        ).get_key()
        spritesheet_component = SpritesheetComponent(cached_spritesheet_name)
        visual_component = VisualComponent(spritesheet_component, "IDLE")
        visual_component.set_default_animation(
            default_idle_for_entity(spritesheet_component)
        )
        entity_element = ElementWrapper(
            registered_name=f"entity_{id(entity)}",
            grouping_name="ENTITY",
            camera=self.camera,
            spatial_component=SpatialComponent(
                pygame.Rect(self._define_entity_rect(pos)),
                space_mode="WORLD",
                z_order=1,
            ),
            interactable_component=RectangleHitbox(),
            visual_component=visual_component,
            payload=EntityPayload(entity),
        )

        return entity_element

    def squeak_element_creator(
        self, squeak: Squeak, i: int
    ) -> tuple[ElementWrapper, ElementWrapper]:
        squeak_type = squeak.rodent
        assert squeak_type
        sprite_metadata = SQUEAK_IMAGE_METADATA_REGISTRY[squeak_type]
        cached_spritesheet_name = SpritesheetManager.register_spritesheet(
            sprite_metadata
        ).get_key()

        squeak_element_id = f"squeak_{id(squeak)}"

        # Base card rect
        card_rect = CARD_RECT.copy()
        card_rect.y += i * (SQUEAK_HEIGHT + SQUEAK_SPACING)

        squeak_element = ElementWrapper(
            registered_name=squeak_element_id,
            grouping_name="SQUEAK",
            camera=self.camera,
            spatial_component=SpatialComponent(
                card_rect, space_mode="SCREEN", z_order=100
            ),
            interactable_component=RectangleHitbox(),
            is_blocking=False,
            visual_component=VisualComponent(
                SpritesheetComponent(spritesheet_reference=cached_spritesheet_name),
                "NONE",
            ),
            payload=SqueakPayload(squeak),
        )

        # Render cost text
        squeak_cost = squeak.crumb_cost
        squeak_cost_text = italic_bold_arial.render(
            str(squeak_cost), False, pygame.Color(255, 255, 255)
        )
        # Compute cost rect anchored to bottom-right of card
        cost_width, cost_height = squeak_cost_text.get_size()
        PADDING = 5

        # --- Local position relative to the card (bottom-right corner) ---
        cost_rect = pygame.Rect(
            SQUEAK_WIDTH - cost_width - PADDING,
            SQUEAK_HEIGHT - cost_height - PADDING,
            cost_width,
            cost_height,
        )

        # Create cost element
        squeak_cost_element = ElementWrapper(
            registered_name=f"squeakCost_{id(squeak)}",
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
            element_parent=ElementParent(squeak_element_id, "SQUEAK"),
        )

        self.squeak_in_hand.append(f"squeak_{(id(squeak))}")

        return squeak_element, squeak_cost_element

    def _select_deselect_logic(
        self,
        saved_key: SavedKey,
        element_id: str | None,
        deselect_on_repeat_selection: bool,
        trigger_anim: bool = True,
    ) -> None:
        if element_id:
            if element_id.split("_")[0] == saved_key.value.lower():
                saved_element_id = self.saved_element_ids[saved_key]
                if not saved_element_id:
                    self._selection(saved_key, element_id, trigger_anim)
                else:
                    if saved_element_id == element_id:
                        if deselect_on_repeat_selection:
                            self._deselection(saved_key, trigger_anim)
                    else:
                        self._deselection(saved_key)
                        self._selection(saved_key, element_id, trigger_anim)
        else:
            saved_element_id = self.saved_element_ids[saved_key]
            if saved_element_id:
                self._deselection(saved_key, trigger_anim)

    def _selection(
        self, saved_key: SavedKey, element_id: str, trigger_anim: bool = True
    ) -> None:
        self.saved_element_ids[saved_key] = element_id
        if not element_id:
            return

        element = self._element_manager.get_element_wrapper(element_id, saved_key.value)

        if not trigger_anim:
            return

        if element and element.visual_component:
            vis = element.visual_component
            if vis and vis.spritesheet_component:
                vis.queue_override_animation(
                    on_select_color_fade_in(
                        vis.spritesheet_component,
                        color=pygame.Color(255, 255, 255),
                    )
                )

    def _deselection(
        self, saved_element_key: SavedKey, trigger_anim: bool = True
    ) -> None:
        element_id, element_type = (
            self.saved_element_ids[saved_element_key],
            saved_element_key.value,
        )
        if not element_id:
            return

        element = self._element_manager.get_element_wrapper(element_id, element_type)

        if not trigger_anim:
            return

        if element and element.visual_component:
            vis = element.visual_component
            if vis and vis.spritesheet_component:
                vis.queue_override_animation(
                    on_select_color_fade_out(
                        vis.spritesheet_component,
                        color=pygame.Color(255, 255, 255),
                    )
                )

        self.saved_element_ids[saved_element_key] = None

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

    def _get_ability_id(self, msg: pygame.event.Event) -> int:
        ability_button_elem_id = self.get_leaf_object_id(self._get_element_id(msg))
        if ability_button_elem_id:
            return int(ability_button_elem_id.split("_")[1])
        else:
            raise ValueError("Ability button elem id is None.")

    # region Element Definition Helpers

    def _define_tile_rect(self, tile: Tile) -> tuple[float, float, float, float]:
        """Given a Tile, return its bounding rectangle as (x, y, width, height)."""
        pixel_x, pixel_y = tile.coord.to_pixel(*TYPICAL_TILE_SIZE, is_bounding_box=True)
        width, height = TYPICAL_TILE_SIZE
        return (pixel_x, pixel_y, width, height)

    def _define_entity_rect(self, pos: OddRCoord) -> tuple[float, float, float, float]:
        """Given an Entity, return its bounding rectangle as (x, y, width, height)."""
        pixel_x, pixel_y = pos.to_pixel(*TYPICAL_TILE_SIZE, is_bounding_box=True)
        width, height = (40, 40)  # Placeholder size for entity
        return (pixel_x, pixel_y, width, height)

    # endregion
