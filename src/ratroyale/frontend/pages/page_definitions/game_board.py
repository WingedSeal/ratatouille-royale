import pygame

from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.input_token import (
    get_gesture_data,
    get_id,
    get_payload_from_msg,
)
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.visual_token import *
from ratroyale.frontend.gesture.gesture_data import GestureType
from ratroyale.event_tokens.payloads import (
    SqueakPlacementPayload,
    SqueakPayload,
    EntityMovementPayload,
    SkillTargetingPayload,
    EntityDamagedPayload,
)

from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.event_binder import (
    input_event_bind,
    callback_event_bind,
    game_event_bind,
    SpecialInputScope,
)
from ratroyale.frontend.pages.page_managers.page_registry import register_page


from ratroyale.frontend.pages.page_elements.element import (
    ElementWrapper,
)
from ratroyale.frontend.pages.page_elements.element_group import (
    HitTestPolicy,
)


from ratroyale.frontend.pages.page_elements.spatial_component import (
    SpatialComponent,
    Camera,
)
from ratroyale.backend.hexagon import OddRCoord


from ratroyale.event_tokens.payloads import (
    TilePayload,
    EntityPayload,
    GameSetupPayload,
    PlayableTilesPayload,
    GameOverPayload,
    AbilityTargetPayload,
)
from ratroyale.backend.game_event import (
    EndTurnEvent,
    EntitySpawnEvent,
    EntityMoveEvent,
    CrumbChangeEvent,
    SqueakDrawnEvent,
)
from ratroyale.backend.tile import Tile

from enum import Enum, auto

from ..page_elements.preset_elements.entity_element import EntityElement
from ..page_elements.preset_elements.squeak_element import SqueakElement
from ..page_elements.preset_elements.tile_mask_element import TileMaskElement
from ..page_elements.preset_elements.feature_element import FeatureElement
from ..page_elements.preset_elements.tilemap_element import ChunkedTileMapElement
from ratroyale.backend.entity import Entity
from ratroyale.backend.side import Side

from ratroyale.backend.entity import SkillTargeting

from typing import Iterable


# from backend.game_event import GameEvent, EntityDamagedEvent

# Load a font, size 48, italic
italic_bold_arial = pygame.font.SysFont("Arial", 48, bold=True, italic=True)


class GameState(Enum):
    PLAY = auto()
    WAIT = auto()
    SKILL_TARGETING = auto()
    MOVEMENT_TARGETING = auto()


@register_page
class GameBoard(Page):
    def __init__(
        self, coordination_manager: CoordinationManager, camera: Camera
    ) -> None:
        super().__init__(coordination_manager, camera)
        self.squeak_in_hand: list[str] = []
        self.hand_slots_element: list[str] = []

        self.coord_to_tile_mapping: dict[OddRCoord, tuple[str, str, str]] = {}
        """Maps coord to HOVERMASK, SELECTMASK, and AVAILABLEMASK"""
        self.entity_to_element_id_mapping: dict[Entity, str] = {}

        self.temp_skill_target_count: int = 0
        self.temp_skill_entity_source: Entity | None = None

        self.is_player_1_now: bool = True
        self.player_1_side: Side = Side.RAT
        self.is_playing_with_ai: bool = True

        self.game_state: GameState = GameState.PLAY

    def on_open(self) -> None:
        self.post(GameManagerEvent(game_action="start_game"))

    def define_initial_gui(self) -> list[ElementWrapper]:
        return []

    # region Game Event Callbacks

    @game_event_bind(EndTurnEvent)
    def end_turn_event(self, event: EndTurnEvent) -> None:
        self.is_player_1_now = not event.is_from_first_turn_side

    @game_event_bind(EntitySpawnEvent)
    def entity_spawn_event(self, event: EntitySpawnEvent) -> None:
        """Handle spawning entity from backend."""
        entity = event.entity
        entity_element = EntityElement(entity, self.camera)
        temp_stat = entity_element._temp_stat_generators()
        self.setup_elements([entity_element, *temp_stat])
        self.entity_to_element_id_mapping[entity] = entity_element.registered_name

    @game_event_bind(EntityMoveEvent)
    def entity_move_event(self, event: EntityMoveEvent) -> None:
        entity = event.entity
        path = event.path

        entity_id = self.entity_to_element_id_mapping[entity]
        entity_element = self.get_element(entity_id, "ENTITY", EntityElement)
        entity_element.move_entity(path)

    @game_event_bind(CrumbChangeEvent)
    def crumb_change_event(self, event: CrumbChangeEvent) -> None:
        new_crumbs = event.new_crumbs
        for squeak_id in self.squeak_in_hand:
            squeak_element = self._element_manager.get_element_with_typecheck(
                squeak_id, SqueakElement
            )
            squeak_element.decide_interactivity(new_crumbs)
        pass

    @game_event_bind(SqueakDrawnEvent)
    def squeak_drawn_event(self, event: SqueakDrawnEvent) -> None:
        # Skip drawing AI's cards
        if self.is_playing_with_ai and not self.is_player_1_now:
            return

        squeak = event.squeak
        hand_index = event.hand_index
        squeak_element = SqueakElement(
            squeak, hand_index, self.camera, italic_bold_arial
        )
        squeak_cost_element = squeak_element.create_cost_element()
        squeak_name_element = squeak_element._temp_name_generator()
        self.setup_elements([squeak_element, squeak_cost_element, squeak_name_element])

        assert isinstance(squeak_element, SqueakElement)
        self.squeak_in_hand.insert(hand_index, squeak_element.registered_name)

    # endregion

    # region Modified Callbacks from Backend

    @callback_event_bind("start_game")
    def _start_game(self, msg: PageCallbackEvent) -> None:
        """Handle the response from starting a game."""

        if msg.success and msg.payload:
            payload = msg.payload
            assert isinstance(payload, GameSetupPayload)
            self.player_1_side = payload.player_1_side
            board = payload.board
            element_configs: list[ElementWrapper] = []
            tiles = board.tiles
            self.is_playing_with_ai = payload.playing_with_ai

            CHUNK_SIZE = 20

            # Create chunked tilemaps
            for row_start in range(0, len(tiles), CHUNK_SIZE):
                for col_start in range(0, len(tiles[0]), CHUNK_SIZE):
                    sub_grid = [
                        row[col_start : col_start + CHUNK_SIZE]
                        for row in tiles[row_start : row_start + CHUNK_SIZE]
                    ]
                    chunk = ChunkedTileMapElement(sub_grid, self.camera)
                    element_configs.append(chunk)

            # Create tile groups with appropriate Hittest policies first.
            group_names = ["SELECTMASK", "HOVERMASK", "AVAILABLEMASK"]
            for name in group_names:
                self._element_manager.create_group(name, HitTestPolicy.HEXGRID, 50)

            for tile_row in tiles:
                for tile in tile_row:
                    if tile:
                        coord = tile.coord

                        tile_hover_mask_element = TileMaskElement(
                            tile, self.camera, "HOVERMASK", 50, pygame.Color(255, 0, 0)
                        )

                        tile_select_mask_element = TileMaskElement(
                            tile,
                            self.camera,
                            "SELECTMASK",
                            51,
                            pygame.Color(0, 255, 255),
                        )

                        tile_available_mask_element = TileMaskElement(
                            tile,
                            self.camera,
                            "AVAILABLEMASK",
                            49,
                            pygame.Color(0, 255, 0),
                        )

                        self.coord_to_tile_mapping[coord] = (
                            tile_hover_mask_element.get_registered_name(),
                            tile_select_mask_element.get_registered_name(),
                            tile_available_mask_element.get_registered_name(),
                        )

                        element_configs.append(tile_hover_mask_element)
                        element_configs.append(tile_select_mask_element)
                        element_configs.append(tile_available_mask_element)

            features = board.cache.features

            for feature in features:
                coord_list = feature.shape
                if coord_list:
                    for coord in coord_list:
                        feature_element = FeatureElement(feature, coord, self.camera)
                        element_configs.append(feature_element)

            squeak_list = payload.hand_squeaks

            for i, squeak in enumerate(squeak_list):
                squeak_element = SqueakElement(
                    squeak, i, self.camera, italic_bold_arial
                )
                squeak_cost_element = squeak_element.create_cost_element()
                squeak_name_element = squeak_element._temp_name_generator()

                card_rect = squeak_element.spatial_component.get_screen_rect(
                    self.camera
                )

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
                self.squeak_in_hand.insert(i, squeak_element.ids[0])

                element_configs.append(squeak_element)
                element_configs.append(squeak_cost_element)
                element_configs.append(squeak_name_element)
                element_configs.append(slot)

            self.setup_elements(element_configs)

            for squeak_id in self.squeak_in_hand:
                squeak_element = self.get_element(squeak_id, "SQUEAK", SqueakElement)

        else:
            raise RuntimeError(f"Failed to start game: {msg.error_msg}")

    @callback_event_bind("can_show_skill_panel_or_not")
    def can_show_skill_panel_or_not_response(self, msg: PageCallbackEvent) -> None:
        if msg.success and msg.payload:
            payload = get_payload_from_msg(msg, EntityPayload)
            assert payload
            if payload.entity.side != self.player_1_side:
                return

            self.post(PageCallbackEvent("can_show_skill_panel"))

    @callback_event_bind("handle_squeak_placable_tiles")
    def _handle_squeak_placable_tiles(self, msg: PageCallbackEvent) -> None:
        """Handle squeak placable tiles from backend."""
        if msg.success and msg.payload:
            assert isinstance(msg.payload, PlayableTilesPayload)
            coord_list = msg.payload.coord_list
            self.set_available_tiles(coord_list)

    @callback_event_bind("squeak_drawn")
    def _squeak_drawn(self, msg: PageCallbackEvent) -> None:
        if msg.success and msg.payload and self.game_state == GameState.PLAY:
            assert isinstance(msg.payload, SqueakPayload)
            squeak = msg.payload.squeak
            hand_index = msg.payload.hand_index
            squeak_element = SqueakElement(
                squeak, hand_index, self.camera, italic_bold_arial
            )
            squeak_cost_element = squeak_element.create_cost_element()
            squeak_name_element = squeak_element._temp_name_generator()
            self.setup_elements(
                [squeak_element, squeak_cost_element, squeak_name_element]
            )

            assert isinstance(squeak_element, SqueakElement)
            self.squeak_in_hand.insert(hand_index, squeak_element.registered_name)

    @callback_event_bind("reachable_coords")
    def _handle_rodent_reachable_tiles(self, msg: PageCallbackEvent) -> None:
        """Handle rodent movable tiles from backend."""
        if msg.success and msg.payload:
            assert isinstance(msg.payload, EntityMovementPayload)
            coord_list = msg.payload.coord_list
            entity = msg.payload.entity
            self.temp_skill_entity_source = entity
            self.set_available_tiles(coord_list)
            self.select_entity(entity)

            self.game_state = GameState.MOVEMENT_TARGETING

    # TODO: make animation sequential per element
    @callback_event_bind("move_entity")
    def _handle_move_entity(self, msg: PageCallbackEvent) -> None:
        if msg.success and msg.payload:
            assert isinstance(msg.payload, EntityMovementPayload)
            entity = msg.payload.entity
            path = msg.payload.coord_list

            entity_id = self.entity_to_element_id_mapping[entity]
            entity_element = self.get_element(entity_id, "ENTITY", EntityElement)
            entity_element.move_entity(path)

    @callback_event_bind("skill_targeting")
    def _handle_skill_targeting(self, msg: PageCallbackEvent) -> None:
        if msg.success and msg.payload:
            self.game_state = GameState.SKILL_TARGETING
            self._element_manager.deselect_all("SELECTMASK")

            assert isinstance(msg.payload, SkillTargetingPayload)

            info = msg.payload.skill_targeting
            if isinstance(info, SkillTargeting):
                self._element_manager.set_max_selectable(
                    "SELECTMASK", info.target_count
                )
                self.set_available_tiles(info.available_targets)
                self.temp_skill_target_count = info.target_count
            else:
                # TODO: relay information to alert page
                print(info)

    @callback_event_bind("entity_damaged")
    def _handle_entity_damaged(self, msg: PageCallbackEvent) -> None:
        if msg.success and msg.payload:
            assert isinstance(msg.payload, EntityDamagedPayload)
            payload = msg.payload

            entity = payload.entity

            entity_id = self.entity_to_element_id_mapping[entity]
            entity_element = self.get_element(entity_id, "ENTITY", EntityElement)

            entity_element.on_hurt()

    @callback_event_bind("entity_died")
    def _handle_entity_died(self, msg: PageCallbackEvent) -> None:
        if msg.success and msg.payload:
            assert isinstance(msg.payload, EntityPayload)
            payload = msg.payload

            entity = payload.entity

            entity_id = self.entity_to_element_id_mapping[entity]

            self.entity_to_element_id_mapping.pop(entity)
            self._element_manager.remove_element(entity_id)

    @callback_event_bind("game_over")
    def _handle_game_over(self, msg: PageCallbackEvent) -> None:
        if msg.success and msg.payload:
            assert isinstance(msg.payload, GameOverPayload)
            payload = msg.payload

            self.post(PageNavigationEvent([(PageNavigation.OPEN, "GameOver")]))
            self.post(PageCallbackEvent("who_won", payload=payload))

    @callback_event_bind("skill_canceled")
    def _handle_skill_canceled(self, msg: PageCallbackEvent) -> None:
        if msg.success:
            self.clear_selections()

    @callback_event_bind("entity_data")
    def center_on_entity(self, msg: PageCallbackEvent) -> None:
        """Upon inspecting entity, center the camera onto the entity's occupied tile"""
        if msg.success and msg.payload:
            payload = get_payload_from_msg(msg, EntityPayload)
            assert payload
            entity_id = self.entity_to_element_id_mapping[payload.entity]
            entity_elem_wrapper = self._element_manager.get_element(entity_id)
            spatial = entity_elem_wrapper.spatial_component.get_screen_rect(self.camera)
            self.camera.move_to(*self.camera.screen_to_world(spatial.x, spatial.y))

    # endregion

    # region Tile Related Events

    @input_event_bind("SELECTMASK", GestureType.CLICK.to_pygame_event())
    def on_tile_click(self, msg: pygame.event.Event) -> None:
        id = get_id(msg)
        assert id
        if self.game_state == GameState.PLAY:
            self.play_state_tile_interaction(id)
        elif self.game_state == GameState.SKILL_TARGETING:
            targeting_done = self.skill_targeting_state_tile_interaction(id)
            self.game_state = GameState.PLAY if targeting_done else self.game_state
        elif self.game_state == GameState.MOVEMENT_TARGETING:
            targeting_done = self.movement_targeting_state_tile_interaction(id)
            self.game_state = GameState.PLAY if targeting_done else self.game_state

    def play_state_tile_interaction(self, id: str) -> None:
        """Selects or toggle tiles, and send data to GameInfo page"""
        tile_element = self._element_manager.toggle_element(id)
        tiles = self.get_selected_tiles()
        if tiles and tile_element:
            self.post(PageCallbackEvent("tile_selected", payload=TilePayload(tiles[0])))
        else:
            self.post(PageCallbackEvent("tile_deselected"))

    def skill_targeting_state_tile_interaction(self, id: str) -> bool:
        # Tiles can only be selected if they are in the available options.
        hovered_tile = self.get_hover_tiles()[0]
        available_tiles = self.get_available_tiles()
        if hovered_tile in available_tiles:
            self._element_manager.select_element(id)
            selected_tiles = self.get_selected_tiles()

            # If the player has chosen enough tiles for the ability, it activates immediately.
            if len(selected_tiles) == self.temp_skill_target_count:
                coord_list = [tile.coord for tile in selected_tiles]
                self.post(
                    GameManagerEvent(
                        "target_selected", AbilityTargetPayload(coord_list)
                    )
                )

                # Clean up highlight effects, close SelectTargetPrompt page, and set self's state to PLAY
                self.clear_selections()
                self.post(
                    PageNavigationEvent(
                        [(PageNavigation.CLOSE, "SelectTargetPromptPage")]
                    )
                )

                return True

        return False

    def movement_targeting_state_tile_interaction(self, id: str) -> bool:
        # Tiles can only be selected if they are in the available options.
        hovered_tile = self.get_hover_tiles()[0]
        available_tiles = self.get_available_tiles()
        if hovered_tile in available_tiles:
            self._element_manager.select_element(id)
            selected_tile_coord = self.get_selected_tiles()[0].coord
            assert self.temp_skill_entity_source, selected_tile_coord

            self.post(
                GameManagerEvent(
                    "resolve_movement",
                    EntityMovementPayload(
                        self.temp_skill_entity_source, [selected_tile_coord]
                    ),
                )
            )

            # Clean up highlight effects, close SelectTargetPrompt page, clear temp selected entity and set self's state to PLAY
            self.clear_selections()
            self.post(
                PageNavigationEvent([(PageNavigation.CLOSE, "SelectTargetPromptPage")])
            )
            self.temp_skill_entity_source = None

            return True
        return False

    @input_event_bind("HOVERMASK", GestureType.HOVER.to_pygame_event())
    def _tile_hover(self, msg: pygame.event.Event) -> None:
        id = get_id(msg)
        assert id
        self._element_manager.select_element(id)
        tile_payload = get_payload_from_msg(msg, TilePayload)
        self.post(PageCallbackEvent("tile_hovered", payload=tile_payload))

    @input_event_bind(SpecialInputScope.UNCONSUMED, GestureType.HOVER.to_pygame_event())
    def _hovering_nothing(self, msg: pygame.event.Event) -> None:
        print("hello")
        self._element_manager.deselect_all("HOVERMASK")
        self.post(PageCallbackEvent("no_hovered"))

    @input_event_bind("TILEMAP", GestureType.HOVER.to_pygame_event())
    def tile_map_hovering_test(self, msg: pygame.event.Event) -> None:
        print("IM PISSED")

    # endregion

    # region Entity Related Events

    # endregion

    # region Squeak Related Events

    @input_event_bind("squeak", GestureType.DRAG_START.to_pygame_event())
    def squeak_drag_start(self, msg: pygame.event.Event) -> None:
        squeak_element_id = get_id(msg)
        gesture_data = get_gesture_data(msg)
        assert squeak_element_id
        self._element_manager.select_element(squeak_element_id)
        squeak_elements = self._element_manager.get_element(squeak_element_id)
        assert squeak_elements

        squeak_elements.spatial_component.center_to_screen_pos(
            gesture_data.mouse_pos, self.camera
        )

        squeak = squeak_elements.get_payload(SqueakPayload)
        self.post(
            GameManagerEvent(game_action="get_squeak_placable_tiles", payload=squeak)
        )

    # endregion

    # region Dragging logic

    # Called while dragging; moves element regardless of hitbox
    @input_event_bind(SpecialInputScope.GLOBAL, GestureType.DRAG.to_pygame_event())
    def _on_drag(self, msg: pygame.event.Event) -> None:
        squeak_element = self._element_manager.get_selected_elements("SQUEAK")
        gesture_data = get_gesture_data(msg)

        if squeak_element and gesture_data.mouse_pos:
            squeak_element[0].spatial_component.center_to_screen_pos(
                gesture_data.mouse_pos, self.camera
            )
        else:
            if self.game_state is not GameState.SKILL_TARGETING:
                self.camera.drag_to(pygame.mouse.get_pos())
            return

    @input_event_bind("SELECTMASK", GestureType.DRAG.to_pygame_event())
    def _on_drag_tile(self, msg: pygame.event.Event) -> None:
        if self.game_state not in (
            GameState.MOVEMENT_TARGETING,
            GameState.SKILL_TARGETING,
        ):
            tile_mask_id = get_id(msg)
            assert tile_mask_id
            self._element_manager.select_element(tile_mask_id)

    @input_event_bind(SpecialInputScope.GLOBAL, GestureType.DRAG_END.to_pygame_event())
    def _on_drag_end(self, msg: pygame.event.Event) -> None:
        if self.game_state not in (
            GameState.MOVEMENT_TARGETING,
            GameState.SKILL_TARGETING,
        ):
            selected_squeaks = self._element_manager.get_selected_elements("SQUEAK")

            selected_tiles = self.get_selected_tiles()
            available_tiles = self.get_available_tiles()

            if selected_tiles and selected_squeaks:
                # Check if selected tiles are valid or not and return to hand if not
                if selected_tiles[0] not in available_tiles:
                    self.return_squeak_to_hand(selected_squeaks[0])
                else:
                    self.trigger_squeak_placement(
                        selected_squeaks[0].registered_name, selected_tiles[0].coord
                    )
            else:
                if selected_squeaks:
                    self.return_squeak_to_hand(selected_squeaks[0])

            self._element_manager.deselect_all("SELECTMASK")
            self._element_manager.deselect_all("AVAILABLEMASK")

        self.camera.end_drag()

    # endregion

    # region Camera Zooming Logic

    @input_event_bind(SpecialInputScope.GLOBAL, pygame.MOUSEWHEEL)
    def _on_scroll(self, msg: pygame.event.Event) -> None:
        if msg.y == 1:
            self.camera.zoom_at(self.camera.scale + 0.1, pygame.mouse.get_pos())
        elif msg.y == -1:
            self.camera.zoom_at(self.camera.scale - 0.1, pygame.mouse.get_pos())

    # endregion

    # region UTILITY METHODS

    def select_entity(self, entity: Entity) -> None:
        entity_elem_id = self.entity_to_element_id_mapping[entity]
        self._element_manager.select_element(entity_elem_id)

    def deselect_entity(self, entity: Entity) -> None:
        entity_elem_id = self.entity_to_element_id_mapping[entity]
        self._element_manager.deselect_element(entity_elem_id)

    def clear_selections(self) -> None:
        self._element_manager.deselect_all("SELECTMASK")
        self._element_manager.deselect_all("AVAILABLEMASK")
        self._element_manager.deselect_all("ENTITY")
        self.post(PageCallbackEvent("tile_deselected"))

    def get_selected_tiles(self) -> list[Tile]:
        tiles = []
        tile_masks = self._element_manager.get_selected_elements("SELECTMASK")
        for tile_elem in tile_masks:
            tiles.append(tile_elem.get_payload(TilePayload).tile)
        return tiles

    def get_available_tiles(self) -> list[Tile]:
        tiles = []
        tile_mask_elements = self._element_manager.get_selected_elements(
            "AVAILABLEMASK"
        )
        for tile_elem in tile_mask_elements:
            tiles.append(tile_elem.get_payload(TilePayload).tile)
        return tiles

    def get_hover_tiles(self) -> list[Tile]:
        tiles = []
        tile_mask_elements = self._element_manager.get_selected_elements("HOVERMASK")
        for tile_elem in tile_mask_elements:
            tiles.append(tile_elem.get_payload(TilePayload).tile)
        return tiles

    def set_available_tiles(self, coord_list: Iterable[OddRCoord]) -> None:
        items = list(coord_list)
        length = len(items)
        self._element_manager.set_max_selectable("AVAILABLEMASK", length)

        for coord in items:
            if coord in self.coord_to_tile_mapping:
                tile_id = self.coord_to_tile_mapping[coord][2]
                self._element_manager.select_element(tile_id)

    def trigger_squeak_placement(
        self, selected_squeak_id: str, tile_coord: OddRCoord
    ) -> None:
        """Trigger the squeak placement animation."""
        self.post(
            GameManagerEvent(
                game_action="squeak_tile_interaction",
                payload=SqueakPlacementPayload(
                    hand_index=self.squeak_in_hand.index(selected_squeak_id),
                    tile_coord=tile_coord,
                ),
            )
        )
        # Kill the squeak element after placement
        self._element_manager.remove_element(selected_squeak_id)
        # Remove selected squeak element id from saved keys & hand list
        self.squeak_in_hand.remove(selected_squeak_id)

    def return_squeak_to_hand(self, squeak_element: ElementWrapper) -> None:
        """Return the squeak element back to the player's hand."""
        squeak_hand_index = self.squeak_in_hand.index(squeak_element.registered_name)
        hand_slot_id = self.hand_slots_element[squeak_hand_index]
        hand_slot_element = self.get_element(hand_slot_id, "HANDSLOT", ElementWrapper)
        target_rect = hand_slot_element.spatial_component.get_screen_rect(self.camera)
        assert isinstance(squeak_element, SqueakElement)
        self._element_manager.deselect_element(squeak_element.registered_name)
        squeak_element.return_to_position(target_rect)

    # endregion

    # endregion
