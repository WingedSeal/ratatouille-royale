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
)

from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.event_binder import (
    input_event_bind,
    callback_event_bind,
    game_event_bind,
    visual_event_bind,
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
    AbilityTargetPayload,
)
from ratroyale.backend.game_event import (
    EndTurnEvent,
    EntitySpawnEvent,
    EntityMoveEvent,
    CrumbChangeEvent,
    SqueakDrawnEvent,
    EntityDamagedEvent,
    EntityDieEvent,
    GameOverEvent,
    FeatureDamagedEvent,
    FeatureDieEvent,
    GameEvent,
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
    PLAYER1 = auto()
    PLAYER2 = auto()
    SKILL_TARGETING = auto()
    MOVEMENT_TARGETING = auto()


@register_page
class GameBoard(Page):
    def __init__(
        self, coordination_manager: CoordinationManager, camera: Camera
    ) -> None:
        super().__init__(coordination_manager, camera)
        self.player_1_squeaks: list[str] = []
        self.player_2_squeaks: list[str] = []
        self.hand_slots_element: list[str] = []
        self.hiding_slots_element: list[str] = []

        self.coord_to_tile_mapping: dict[OddRCoord, tuple[str, str, str]] = {}
        """Maps coord to HOVERMASK, SELECTMASK, and AVAILABLEMASK"""
        self.entity_to_element_id_mapping: dict[Entity, str] = {}
        self.feature_to_element_id_mapping: dict[int, list[str]] = {}

        self.temp_skill_target_count: int = 0
        self.temp_skill_entity_source: Entity | None = None

        self.is_player_1_now: bool = True
        self.player_1_side: Side = Side.RAT
        self.is_playing_with_ai: bool = True
        self.is_game_over: bool = False

        self.ai_did_something: bool = False
        # HACK: previous "vs. AI turn switching" logic relied on the AI player playing anything to trigger end of animation.
        # If the ai played nothing, the logic breaks and the human player never gets to see their hand again until the AI decides to play something again.

        self.game_state: GameState = GameState.PLAYER1

    def on_open(self) -> None:
        self.post(GameManagerEvent(game_action="start_game"))

    def define_initial_gui(self) -> list[ElementWrapper]:
        return []

    # region Visual Event Callbacks

    @visual_event_bind("anim_queue_finished")
    def anim_queue_finished(self, msg: VisualManagerEvent) -> None:
        if self.is_game_over:
            self.post(PageNavigationEvent([(PageNavigation.OPEN, "GameOver")]))
            self.open_page("GameOver")
        if self.game_state == GameState.PLAYER2 and self.is_playing_with_ai:
            self.game_state = GameState.PLAYER1
            self.show_player_hand(1)
            self.hide_player_hand(2)

    @visual_event_bind("entity_die_finished")
    @visual_event_bind("particle_anim_finished")
    def entity_die_finished(self, msg: VisualManagerEvent) -> None:
        entity_name = msg.element_name
        self._element_manager.remove_element(entity_name)

    # endregion

    # region Game Event Callbacks

    @game_event_bind(EndTurnEvent)
    def end_turn_event(self, event: EndTurnEvent) -> None:
        self.clear_selections()
        self.is_player_1_now = not event.is_from_player_1_side

        # If not playing with an AI, switches player hands.
        if not self.is_playing_with_ai:
            if not self.is_player_1_now:
                self.game_state = GameState.PLAYER2
                self.hide_player_hand(1)
                self.show_player_hand(2)
            else:
                self.game_state = GameState.PLAYER1
                self.hide_player_hand(2)
                self.show_player_hand(1)
        else:
            if not self.is_player_1_now:
                self.ai_did_something = False
                self.game_state = GameState.PLAYER2
                self.hide_player_hand(1)
            else:
                if not self.ai_did_something:
                    self.game_state = GameState.PLAYER1
                    self.show_player_hand(1)

        entities = self._element_manager.get_group("ENTITY").get_all_elements()
        for entity in entities:
            assert isinstance(entity, EntityElement)
            entity.update_move_stamina()

    @game_event_bind(GameEvent)
    def generic_game_event_test(self, event: GameEvent) -> None:
        if self.is_playing_with_ai and not self.is_player_1_now:
            # Only count real actions
            if not isinstance(event, (CrumbChangeEvent, EndTurnEvent)):
                self.ai_did_something = True

    @game_event_bind(EntitySpawnEvent)
    def entity_spawn_event(self, event: EntitySpawnEvent) -> None:
        """Handle spawning entity from backend."""
        entity = event.entity
        entity_element = EntityElement(entity, self.camera)
        temp_stat = entity_element.stat_elements()
        self.setup_elements([entity_element, *temp_stat])
        self.entity_to_element_id_mapping[entity] = entity_element.registered_name

        anim = entity_element.on_spawn()
        self.queue_animation([anim])

    @game_event_bind(EntityMoveEvent)
    def entity_move_event(self, event: EntityMoveEvent) -> None:
        entity = event.entity
        path = event.path

        entity_id = self.entity_to_element_id_mapping[entity]
        entity_element = self.get_element(entity_id, "ENTITY", EntityElement)
        entity_element.update_move_stamina()
        anim_set = entity_element.move_entity(path)
        self.queue_animation(anim_set)

    @game_event_bind(CrumbChangeEvent)
    def crumb_change_event(self, event: CrumbChangeEvent) -> None:
        new_crumbs = event.new_crumbs
        targeted_set = self.get_targeted_set()

        for squeak_id in targeted_set:
            squeak_element = self._element_manager.get_element_with_typecheck(
                squeak_id, SqueakElement
            )
            squeak_element.decide_interactivity(new_crumbs)

    @game_event_bind(SqueakDrawnEvent)
    def squeak_drawn_event(self, event: SqueakDrawnEvent) -> None:
        # Skip drawing AI's cards
        if self.is_playing_with_ai and not self.is_player_1_now:
            return

        targeted_set = self.get_targeted_set()

        squeak = event.squeak
        hand_index = event.hand_index
        squeak_element = SqueakElement(
            squeak, hand_index, self.camera, italic_bold_arial
        )
        squeak_cost_element = squeak_element.create_cost_element()
        squeak_name_element = squeak_element._temp_name_generator()
        self.setup_elements([squeak_element, squeak_cost_element, squeak_name_element])

        assert isinstance(squeak_element, SqueakElement)
        targeted_set.insert(hand_index, squeak_element.registered_name)

        print("INSERTION:", self.game_state, squeak_element.registered_name)

    @game_event_bind(EntityDamagedEvent)
    def entity_damaged_event(self, event: EntityDamagedEvent) -> None:
        """Plays entity damaged animation."""
        entity = event.entity

        entity_id = self.entity_to_element_id_mapping[entity]
        entity_element = self.get_element(entity_id, "ENTITY", EntityElement)

        anim_set = entity_element.on_hurt()
        self.queue_animation([anim_set])

        hurt_particle = entity_element.hurt_particle(event.hp_loss)
        self.setup_elements([hurt_particle])

    @game_event_bind(EntityDieEvent)
    def entity_die_event(self, event: EntityDieEvent) -> None:
        entity = event.entity

        entity_element_id = self.entity_to_element_id_mapping.pop(entity)
        entity_element = self._element_manager.get_element_with_typecheck(
            entity_element_id, EntityElement
        )
        anim = entity_element.on_die()
        self.queue_animation([anim])

    @game_event_bind(FeatureDamagedEvent)
    def feature_damaged_event(self, event: FeatureDamagedEvent) -> None:
        feature = event.feature

        feature_element_ids = self.feature_to_element_id_mapping[id(feature)]
        for feature_element_id in feature_element_ids:
            feature_element = self._element_manager.get_element_with_typecheck(
                feature_element_id, FeatureElement
            )

            anim = feature_element.on_damaged()
            self.queue_animation([anim])

            element = feature_element.hurt_particle(event.hp_loss)
            self.setup_elements([element])

    @game_event_bind(FeatureDieEvent)
    def feature_die_event(self, event: FeatureDieEvent) -> None:
        feature = event.feature

        feature_element_ids = self.feature_to_element_id_mapping[id(feature)]
        for feature_element_id in feature_element_ids:
            feature_element = self._element_manager.get_element_with_typecheck(
                feature_element_id, FeatureElement
            )
            anim = feature_element.on_die()
            self.queue_animation([anim])

    @game_event_bind(GameOverEvent)
    def game_over_event(self, event: GameOverEvent) -> None:
        who_won = event.victory_side

        print(who_won)

        self.is_game_over = True

        # self.post(PageNavigationEvent([(PageNavigation.OPEN, "GameOver")]))
        # self.post(PageCallbackEvent("who_won", payload=Game))

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

            CHUNK_SIZE = 16

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
                self._element_manager.create_group(name, HitTestPolicy.HEXGRID, 1)
            squeak_group = "SQUEAK"
            self._element_manager.create_group(squeak_group, hittest_priority=2)

            for tile_row in tiles:
                for tile in tile_row:
                    if tile:
                        coord = tile.coord

                        tile_hover_mask_element = TileMaskElement(
                            tile, self.camera, "HOVERMASK", 50, pygame.Color("cyan")
                        )

                        tile_select_mask_element = TileMaskElement(
                            tile,
                            self.camera,
                            "SELECTMASK",
                            51,
                            pygame.Color("yellow"),
                        )

                        tile_available_mask_element = TileMaskElement(
                            tile,
                            self.camera,
                            "AVAILABLEMASK",
                            49,
                            pygame.Color("green"),
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
                feature_element_ids = []
                coord_list = feature.shape
                if coord_list:
                    for coord in coord_list:
                        feature_element = FeatureElement(feature, coord, self.camera)
                        feature_element_ids.append(feature_element.registered_name)
                        element_configs.append(feature_element)
                self.feature_to_element_id_mapping[id(feature)] = feature_element_ids

            player1_squeak_list = payload.player1_squeaks
            player2_squeak_list = payload.player2_squeaks

            for i, (sq1, sq2) in enumerate(
                zip(player1_squeak_list, player2_squeak_list)
            ):
                # Shared slot geometry
                temp_squeak = SqueakElement(sq1, i, self.camera, italic_bold_arial)
                card_rect = temp_squeak.spatial_component.get_screen_rect(self.camera)
                hide_slot_rect = card_rect.move(-card_rect.width, 0)

                # Shared slot wrappers
                slot_id = f"hand_slot_{i}"
                hide_slot_id = f"hide_slot_{i}"
                slot = ElementWrapper(
                    registered_name=slot_id,
                    grouping_name="HANDSLOT",
                    camera=self.camera,
                    spatial_component=SpatialComponent(
                        local_rect=card_rect, z_order=99
                    ),
                )
                hide_slot = ElementWrapper(
                    registered_name=hide_slot_id,
                    grouping_name="HIDESLOT",
                    camera=self.camera,
                    spatial_component=SpatialComponent(
                        local_rect=hide_slot_rect, z_order=99
                    ),
                )
                self.hand_slots_element.append(slot_id)
                self.hiding_slots_element.append(hide_slot_id)

                # Player 1 squeak (starts visible)
                squeak1 = SqueakElement(sq1, i, self.camera, italic_bold_arial)
                squeak1_cost = squeak1.create_cost_element()
                squeak1_name = squeak1._temp_name_generator()
                self.player_1_squeaks.insert(i, squeak1.ids[0])

                # Player 2 squeak (starts hidden)
                squeak2 = SqueakElement(sq2, i, self.camera, italic_bold_arial)
                squeak2_cost = squeak2.create_cost_element()
                squeak2_name = squeak2._temp_name_generator()
                self.player_2_squeaks.insert(i, squeak2.ids[0])

                # Collect everything
                element_configs += [
                    squeak1,
                    squeak1_cost,
                    squeak1_name,
                    squeak2,
                    squeak2_cost,
                    squeak2_name,
                    slot,
                    hide_slot,
                ]

                print("Player1 Squeak IDs:", squeak1.ids)
                print("Player2 Squeak IDs:", squeak2.ids)

            self.setup_elements(element_configs)

            crumb = payload.starting_crumbs
            for squeak_id in self.player_1_squeaks:
                squeak_element = self._element_manager.get_element_with_typecheck(
                    squeak_id, SqueakElement
                )
                squeak_element.decide_interactivity(crumb)

            self.hide_player_hand(2)

        else:
            raise RuntimeError(f"Failed to start game: {msg.error_msg}")

    @callback_event_bind("can_show_skill_panel_or_not")
    def can_show_skill_panel_or_not_response(self, msg: PageCallbackEvent) -> None:
        if not (msg.success and msg.payload):
            return

        payload = get_payload_from_msg(msg, EntityPayload)
        assert payload

        # Determine which side should be allowed right now
        current_side = (
            self.player_1_side
            if self.is_player_1_now
            else self.player_1_side.other_side()
        )

        # Only allow showing the panel if the entity belongs to the side whose turn it is
        if payload.entity.side != current_side:
            return

        # Post event to actually show panel
        self.post(PageCallbackEvent("can_show_skill_panel"))

    @callback_event_bind("handle_squeak_placable_tiles")
    def _handle_squeak_placable_tiles(self, msg: PageCallbackEvent) -> None:
        """Handle squeak placable tiles from backend."""
        if msg.success and msg.payload:
            assert isinstance(msg.payload, PlayableTilesPayload)
            coord_list = msg.payload.coord_list
            self.set_available_tiles(coord_list)

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
            self.center_on_entity(entity)

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
                source_entity = info.source_enitity
                self.center_on_entity(source_entity)
                self._element_manager.set_max_selectable(
                    "SELECTMASK", info.target_count
                )
                self.set_available_tiles(info.available_targets)
                self.temp_skill_target_count = info.target_count
            else:
                # TODO: relay information to alert page
                print(info)
                self.post(
                    PageNavigationEvent(
                        [(PageNavigation.CLOSE, "SelectTargetPromptPage")]
                    )
                )
                self.clear_selections()
                self.game_state = GameState.PLAYER1

    @callback_event_bind("skill_canceled")
    def _handle_skill_canceled(self, msg: PageCallbackEvent) -> None:
        if msg.success:
            self.clear_selections()
            self.game_state = (
                GameState.PLAYER1 if self.is_player_1_now else GameState.PLAYER2
            )

    @callback_event_bind("entity_data")
    def inspect_entity(self, msg: PageCallbackEvent) -> None:
        """Upon inspecting entity, center the camera onto the entity's occupied tile"""
        if msg.success and msg.payload:
            payload = get_payload_from_msg(msg, EntityPayload)
            assert payload
            self.center_on_entity(payload.entity)

    def center_on_entity(self, entity: Entity) -> None:
        entity_id = self.entity_to_element_id_mapping[entity]
        entity_elem_wrapper = self._element_manager.get_element(entity_id)
        spatial = entity_elem_wrapper.spatial_component.get_screen_rect(self.camera)
        self.camera.move_to(*self.camera.screen_to_world(spatial.x, spatial.y))

    # endregion

    # region Tile Related Events

    @input_event_bind("SELECTMASK", GestureType.CLICK.to_pygame_event())
    def on_tile_click(self, msg: pygame.event.Event) -> None:
        id = get_id(msg)
        assert id
        if self.game_state == GameState.PLAYER1 or (
            self.game_state == GameState.PLAYER2 and not self.is_playing_with_ai
        ):
            self.play_state_tile_interaction(id)
        elif self.game_state == GameState.SKILL_TARGETING:
            targeting_done = self.skill_targeting_state_tile_interaction(id)
            self.game_state = GameState.PLAYER1 if targeting_done else self.game_state
        elif self.game_state == GameState.MOVEMENT_TARGETING:
            targeting_done = self.movement_targeting_state_tile_interaction(id)
            self.game_state = GameState.PLAYER1 if targeting_done else self.game_state

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
    def check_if_hovering_nothing(self, msg: pygame.event.Event) -> None:
        self._element_manager.deselect_all("HOVERMASK")
        self.post(PageCallbackEvent("no_hovered"))

    # endregion

    # region Squeak Related Events

    @input_event_bind("squeak", GestureType.HOLD.to_pygame_event())
    def squeak_hold_inspect(self, msg: pygame.event.Event) -> None:
        squeak_payload = get_payload_from_msg(msg, SqueakPayload)
        self.post(PageNavigationEvent([(PageNavigation.OPEN, "InspectSqueak")]))
        self.post(PageCallbackEvent("squeak_data", payload=squeak_payload))

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
            self.camera.drag_to(pygame.mouse.get_pos())

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

            self.camera.end_drag()  # HACK: Im not sure how but this seems to fix the jumping issue in tandem to the other HACK fix.

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

    def hide_player_hand(self, player: int) -> None:
        if player == 1:
            squeak_list = self.player_1_squeaks
        elif player == 2:
            squeak_list = self.player_2_squeaks
        else:
            return

        for squeak, hide_slot in zip(squeak_list, self.hiding_slots_element):
            squeak_element = self._element_manager.get_element_with_typecheck(
                squeak, SqueakElement
            )
            hide_rect = self._element_manager.get_element(hide_slot).get_absolute_rect()
            squeak_element.move_to_position(hide_rect)

    def show_player_hand(self, player: int) -> None:
        if player == 1:
            squeak_list = self.player_1_squeaks
        elif player == 2:
            squeak_list = self.player_2_squeaks
        else:
            return

        for squeak, hand_slot in zip(squeak_list, self.hand_slots_element):
            squeak_element = self._element_manager.get_element_with_typecheck(
                squeak, SqueakElement
            )
            hand_rect = self._element_manager.get_element(hand_slot).get_absolute_rect()
            squeak_element.move_to_position(hand_rect)

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
        targeted_set = self.get_targeted_set()

        self.post(
            GameManagerEvent(
                game_action="squeak_tile_interaction",
                payload=SqueakPlacementPayload(
                    hand_index=targeted_set.index(selected_squeak_id),
                    tile_coord=tile_coord,
                ),
            )
        )
        # Kill the squeak element after placement
        self._element_manager.remove_element(selected_squeak_id)
        # Remove selected squeak element id from saved keys & hand list
        targeted_set.remove(selected_squeak_id)

        print("REMOVAL:", self.game_state, selected_squeak_id)

    def return_squeak_to_hand(self, squeak_element: ElementWrapper) -> None:
        """Return the squeak element back to the player's hand."""
        targeted_set = self.get_targeted_set()

        squeak_hand_index = targeted_set.index(squeak_element.registered_name)
        hand_slot_id = self.hand_slots_element[squeak_hand_index]
        hand_slot_element = self.get_element(hand_slot_id, "HANDSLOT", ElementWrapper)
        target_rect = hand_slot_element.spatial_component.get_screen_rect(self.camera)
        assert isinstance(squeak_element, SqueakElement)
        self._element_manager.deselect_element(squeak_element.registered_name)
        squeak_element.move_to_position(target_rect)

    def get_targeted_set(self) -> list[str]:
        if self.is_player_1_now:
            return self.player_1_squeaks
        else:
            return self.player_2_squeaks

    # endregion

    # endregion
