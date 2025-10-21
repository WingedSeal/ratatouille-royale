import pygame
import pygame_gui

from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.input_token import get_gesture_data, get_id
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.visual_token import *
from ratroyale.frontend.gesture.gesture_data import GestureType
from ratroyale.event_tokens.payloads import (
    SqueakPlacementPayload,
    SqueakPayload,
    EntityMovementPayload,
    SkillTargetingPayload,
    AbilityTargetPayload,
    EntityDamagedPayload,
    AbilityActivationPayload,
)

from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.event_binder import (
    input_event_bind,
    callback_event_bind,
)
from ratroyale.frontend.pages.page_managers.page_registry import register_page


from ratroyale.frontend.pages.page_elements.element import (
    ElementWrapper,
    ui_element_wrapper,
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
    CrumbUpdatePayload,
    PlayableTiles,
    GameOverPayload,
)
from ratroyale.backend.tile import Tile

from ratroyale.frontend.visual.asset_management.visual_component import VisualComponent
from ratroyale.frontend.visual.asset_management.spritesheet_structure import (
    SpritesheetComponent,
)
from enum import Enum, auto

from ..page_elements.preset_elements.tile_element import TileElement
from ..page_elements.preset_elements.entity_element import EntityElement
from ..page_elements.preset_elements.squeak_element import SqueakElement
from ..page_elements.preset_elements.tile_mask_element import TileMaskElement
from ..page_elements.preset_elements.feature_element import FeatureElement
from ratroyale.backend.entity import Entity
from ratroyale.backend.side import Side

from ratroyale.backend.entity import SkillTargeting

from typing import Iterable


# from backend.game_event import GameEvent, EntityDamagedEvent

# Load a font, size 48, italic
italic_bold_arial = pygame.font.SysFont("Arial", 48, bold=True, italic=True)


class GameState(Enum):
    PLAY = auto()
    MOVEMENT = auto()
    ABILITY = auto()
    WAIT = auto()
    ABILITY_PANEL = auto()


@register_page
class GameBoard(Page):
    def __init__(
        self, coordination_manager: CoordinationManager, camera: Camera
    ) -> None:
        super().__init__(coordination_manager, camera)
        self.squeak_in_hand: list[str] = []
        self.hand_slots_element: list[str] = []

        self.current_crumb: int = 0

        self.coord_to_tile_mapping: dict[OddRCoord, tuple[str, str, str]] = {}
        """Maps coord to HOVERMASK, SELECTMASK, and AVAILABLEMASK"""
        self.entity_to_element_id_mapping: dict[Entity, str] = {}

        self.ability_panel_id: str | None = None
        self.temp_ability_target_count: int = 0

        self.player_1_side: Side = Side.MOUSE

        # TODO: make separate object
        self.game_state: GameState = GameState.PLAY

    def on_open(self) -> None:
        self.post(GameManagerEvent(game_action="start_game"))

    def define_initial_gui(self) -> list[ElementWrapper]:
        return []

    # region Callbacks from Backend

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

            for tile_row in tiles:
                for tile in tile_row:
                    if tile:
                        tile_element = TileElement(tile, self.camera)
                        coord = tile_element.get_coord()

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

                        element_configs.append(tile_element)
                        element_configs.append(tile_hover_mask_element)
                        element_configs.append(tile_select_mask_element)
                        element_configs.append(tile_available_mask_element)

            features = board.cache.features

            for feature in features:
                coord_list = feature.shape
                if coord_list:
                    for coord in coord_list:
                        print("creating features")
                        feature_element = FeatureElement(feature, coord, self.camera)
                        element_configs.append(feature_element)

            starting_crumbs = payload.starting_crumbs
            self.current_crumb = starting_crumbs
            crumb_display_text = italic_bold_arial.render(
                str(starting_crumbs), False, pygame.Color(255, 255, 255)
            )

            crumb_display_rect = pygame.Rect(20, 25, 100, 40)

            # Create cost element
            crumb_display_element = ElementWrapper(
                registered_name="crumb_display",
                grouping_name="UI_ELEMENT",
                camera=self.camera,
                spatial_component=SpatialComponent(
                    crumb_display_rect, space_mode="SCREEN", z_order=102
                ),
                interactable_component=None,
                is_blocking=False,
                visual_component=VisualComponent(
                    SpritesheetComponent(spritesheet_reference=crumb_display_text),
                    "NONE",
                ),
            )

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

            element_configs.append(crumb_display_element)

            end_turn = ui_element_wrapper(
                pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(800 - 150 - 10, 600 - 150 - 10, 150, 40),
                    text="End Turn",
                    manager=self.gui_manager,
                    object_id=pygame_gui.core.ObjectID(
                        class_id="ActionButton", object_id="endturn"
                    ),
                ),
                "end_turn",
                self.camera,
            )

            element_configs.append(end_turn)

            self.setup_elements(element_configs)

            for squeak_id in self.squeak_in_hand:
                squeak_element = self.get_element(squeak_id, "SQUEAK", SqueakElement)
                squeak_element.decide_interactivity(self.current_crumb)

        else:
            raise RuntimeError(f"Failed to start game: {msg.error_msg}")

    @callback_event_bind("crumb_update")
    def _crumb_update(self, msg: PageCallbackEvent) -> None:
        """Handle crumb update from backend."""
        if msg.success and msg.payload and GameState.PLAY:
            assert isinstance(msg.payload, CrumbUpdatePayload)
            new_crumb_amt = msg.payload.new_crumb_amount
            self.current_crumb = new_crumb_amt

            crumb_display_elem = self.get_element(
                "crumb_display", "UI_ELEMENT", ElementWrapper
            )

            crumb_display_text = italic_bold_arial.render(
                str(new_crumb_amt), False, pygame.Color(255, 255, 255)
            )

            vis = crumb_display_elem.visual_component
            assert vis
            spr = vis.spritesheet_component
            assert spr
            spr.spritesheet_reference = crumb_display_text

            # disable interactivity for squeaks whose cost is above new crumb amount
            for squeak_id in self.squeak_in_hand:
                squeak_element = self.get_element(squeak_id, "SQUEAK", SqueakElement)
                squeak_element.decide_interactivity(new_crumb_amt)

    @callback_event_bind("handle_squeak_placable_tiles")
    def _handle_squeak_placable_tiles(self, msg: PageCallbackEvent) -> None:
        """Handle squeak placable tiles from backend."""
        if msg.success and msg.payload:
            assert isinstance(msg.payload, PlayableTiles)
            coord_list = msg.payload.coord_list
            self.set_available_tiles(coord_list)

    @callback_event_bind("spawn_entity")
    def _spawn_entity(self, msg: PageCallbackEvent) -> None:
        """Handle spawning entity from backend."""
        if msg.success and msg.payload:
            assert isinstance(msg.payload, EntityPayload)
            entity = msg.payload.entity
            entity_element = EntityElement(entity, self.camera)
            temp_stat = entity_element._temp_stat_generators()
            self.setup_elements([entity_element, *temp_stat])
            self.entity_to_element_id_mapping[entity] = entity_element.registered_name

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
            squeak_element.decide_interactivity(self.current_crumb)
            self.squeak_in_hand.insert(hand_index, squeak_element.registered_name)

    @callback_event_bind("reachable_coords")
    def _handle_rodent_reachable_tiles(self, msg: PageCallbackEvent) -> None:
        """Handle rodent movable tiles from backend."""
        if msg.success and msg.payload:
            assert isinstance(msg.payload, PlayableTiles)
            coord_list = msg.payload.coord_list
            self.set_available_tiles(coord_list)

            self.game_state = GameState.MOVEMENT

    # TODO: make animation sequential per element
    @callback_event_bind("move_entity")
    def _handle_move_entity(self, msg: PageCallbackEvent) -> None:
        if msg.success and msg.payload:
            assert isinstance(msg.payload, EntityMovementPayload)
            entity = msg.payload.entity
            path = msg.payload.path

            entity_id = self.entity_to_element_id_mapping[entity]
            entity_element = self.get_element(entity_id, "ENTITY", EntityElement)
            entity_element.move_entity(path)

    @callback_event_bind("end_turn")
    def _handle_end_turn(self, msg: PageCallbackEvent) -> None:
        if msg.success:
            if self.game_state == GameState.WAIT:
                self.game_state = GameState.PLAY
            else:
                self.game_state = GameState.WAIT

    @callback_event_bind("skill_targeting")
    def _handle_skill_targeting(self, msg: PageCallbackEvent) -> None:
        if msg.success and msg.payload:
            assert isinstance(msg.payload, SkillTargetingPayload)
            info = msg.payload.skill_targeting
            if isinstance(info, SkillTargeting):
                self._element_manager.set_max_selectable(
                    "SELECTMASK", info.target_count
                )
                self.set_available_tiles(info.available_targets)
                self.temp_ability_target_count = info.target_count
            else:
                print(info)

            self.game_state = GameState.ABILITY

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

            CoordinationManager.put_message(
                PageNavigationEvent([(PageNavigation.OPEN, "GameOver")])
            )
            CoordinationManager.put_message(
                PageCallbackEvent("who_won", payload=payload)
            )

    # endregion

    # region Tile Related Events

    @input_event_bind("SELECTMASK", GestureType.CLICK.to_pygame_event())
    def _on_tile_click(self, msg: pygame.event.Event) -> None:
        id = get_id(msg)
        assert id
        print(self.game_state)
        if self.game_state == GameState.MOVEMENT:
            # Get the entity on the old selected tile first.
            selected_tiles = self.get_selected_tiles()
            selected_entity = selected_tiles[0].entities[0]

            # Then get the target tile
            self._element_manager.select_element(id)
            selected_tiles = self.get_selected_tiles()

            target = selected_tiles[0].coord
            self.coordination_manager.put_message(
                GameManagerEvent(
                    "resolve_movement",
                    EntityMovementPayload(selected_entity, [target]),
                )
            )
            self.game_state = GameState.PLAY

            self._element_manager.deselect_all("SELECTMASK")
            self._element_manager.deselect_all("AVAILABLEMASK")
        elif self.game_state == GameState.ABILITY:

            hovered_tile = self.get_hover_tiles()
            available_tiles = self.get_available_tiles()
            if hovered_tile[0] not in available_tiles:
                return
            self._element_manager.select_element(id)
            selected_tiles = self.get_selected_tiles()
            if len(selected_tiles) == self.temp_ability_target_count:
                selected_coords = []
                for tile in selected_tiles:
                    selected_coords.append(tile.coord)
                target_payload = AbilityTargetPayload(selected_coords)
                self.coordination_manager.put_message(
                    GameManagerEvent("target_selected", target_payload)
                )

                self._element_manager.deselect_all("SELECTMASK")
                self._element_manager.deselect_all("AVAILABLEMASK")

                self.game_state = GameState.PLAY
        elif self.game_state in (GameState.ABILITY_PANEL, GameState.WAIT):
            return
        else:
            if self._display_ability_menu(msg):
                return None
            self._element_manager.toggle_element(id)
            self._close_ability_menu()

    @input_event_bind("HOVERMASK", GestureType.HOVER.to_pygame_event())
    def _tile_hover_test(self, msg: pygame.event.Event) -> None:
        """Test hover event on tile."""
        id = get_id(msg)
        assert id
        self._element_manager.select_element(id)
        # For testing purposes, we just print the hover info
        # Will send data over to player info layer later

    # endregion

    # region Entity Related Events

    # @input_event_bind("SELECTMASK", GestureType.HOLD.to_pygame_event())
    def _display_ability_menu(self, msg: pygame.event.Event) -> bool:
        """Display the ability menu for the selected entity."""

        id = get_id(msg)
        assert id
        self._element_manager.select_element(id)

        tile = self.get_selected_tiles()[0]

        if not tile.entities:
            return False

        entity = tile.entities[0]

        if entity.side != self.player_1_side:
            return False

        entity_id = self.entity_to_element_id_mapping[entity]
        entity_element = self._element_manager.get_element(entity_id)

        # region Create ability panel

        entity_spatial_rect = entity_element.spatial_component.get_screen_rect(
            self.camera
        )
        entity_center_x = entity_spatial_rect.x + entity_spatial_rect.width / 2
        entity_center_y = entity_spatial_rect.y + entity_spatial_rect.height / 2
        self.camera.move_to(
            *self.camera.screen_to_world(entity_center_x, entity_center_y)
        )

        entity_spatial_rect = entity_element.spatial_component.get_screen_rect(
            self.camera
        )
        entity_center_x = entity_spatial_rect.x + entity_spatial_rect.width / 2
        entity_center_y = entity_spatial_rect.y + entity_spatial_rect.height / 2

        panel_width = 160
        panel_x = entity_center_x - panel_width / 2
        panel_y = entity_center_y + entity_spatial_rect.height
        panel_id = "ability_panel"
        self.ability_panel_id = panel_id
        panel_rect = pygame.Rect(
            panel_x, panel_y, panel_width, len(entity.skills) * 30 + 30 + 10
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
            spatial_component=SpatialComponent(
                panel_object.get_abs_rect(), z_order=200
            ),
            interactable_component=panel_object,
            visual_component=VisualComponent(),
            is_blocking=True,
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

        # After all skills, add the "Move" button
        move_button_y = len(entity.skills) * 30  # Position after the last skill
        pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, move_button_y, 150, 30),
            text="Move",
            manager=self.gui_manager,
            container=panel_object,
            object_id=pygame_gui.core.ObjectID(
                class_id="AbilityButton", object_id="ability_-1"
            ),
        )

        self.game_state = GameState.ABILITY_PANEL

        return True
        # endregion

    @input_event_bind("ability", pygame_gui.UI_BUTTON_PRESSED)
    def _activate_ability(self, msg: pygame.event.Event) -> None:
        """Activate selected ability."""
        ability_id = self._get_ability_id(msg)
        tile = self.get_selected_tiles()[0]
        entity = tile.entities[0]
        ability_payload = AbilityActivationPayload(ability_id, entity)
        self.coordination_manager.put_message(
            GameManagerEvent("ability_activation", ability_payload)
        )
        self._close_ability_menu()

    @input_event_bind("endturn", pygame_gui.UI_BUTTON_PRESSED)
    def _end_turn(self, msg: pygame.event.Event) -> None:
        self.coordination_manager.put_message(GameManagerEvent("end_turn"))
        self._element_manager.deselect_all("SELECTMASK")
        self._element_manager.deselect_all("AVAILABLEMASK")
        self._close_ability_menu()

    # endregion

    # region Squeak Related Events

    @input_event_bind("squeak", GestureType.DRAG_START.to_pygame_event())
    def squeak_drag_start(self, msg: pygame.event.Event) -> None:
        squeak_element_id = get_id(msg)
        gesture_data = get_gesture_data(msg)
        assert squeak_element_id
        self._element_manager.select_element(squeak_element_id)
        squeak_elements = self._element_manager.get_selected_elements("SQUEAK")[1]

        if squeak_elements:
            squeak_elements[0].spatial_component.center_to_screen_pos(
                gesture_data.mouse_pos, self.camera
            )

            squeak = squeak_elements[0].get_payload(SqueakPayload)
            self.coordination_manager.put_message(
                GameManagerEvent(
                    game_action="get_squeak_placable_tiles", payload=squeak
                )
            )

    # endregion

    # region Dragging logic

    # Called while dragging; moves element regardless of hitbox
    @input_event_bind(None, GestureType.DRAG.to_pygame_event())
    def _on_drag(self, msg: pygame.event.Event) -> None:
        squeak_element = self._element_manager.get_selected_elements("SQUEAK")[1]
        gesture_data = get_gesture_data(msg)

        if squeak_element and gesture_data.mouse_pos:
            squeak_element[0].spatial_component.center_to_screen_pos(
                gesture_data.mouse_pos, self.camera
            )
        else:
            if self.game_state is not GameState.ABILITY_PANEL:
                self.camera.drag_to(pygame.mouse.get_pos())
            return

    @input_event_bind("SELECTMASK", GestureType.DRAG.to_pygame_event())
    def _on_drag_tile(self, msg: pygame.event.Event) -> None:
        if self.game_state not in (
            GameState.MOVEMENT,
            GameState.ABILITY,
            GameState.ABILITY_PANEL,
        ):
            tile_mask_id = get_id(msg)
            assert tile_mask_id
            self._element_manager.select_element(tile_mask_id)

    @input_event_bind(None, GestureType.DRAG_END.to_pygame_event())
    def _on_drag_end(self, msg: pygame.event.Event) -> None:
        if self.game_state not in (
            GameState.MOVEMENT,
            GameState.ABILITY,
            GameState.ABILITY_PANEL,
        ):
            selected_squeak_id, selected_squeaks = (
                self._element_manager.get_selected_elements("SQUEAK")
            )

            selected_tiles = self.get_selected_tiles()
            available_tiles = self.get_available_tiles()

            if selected_tiles and selected_squeak_id:
                # Check if selected tiles are valid or not and return to hand if not
                if selected_tiles[0] not in available_tiles:
                    self.return_squeak_to_hand(selected_squeaks[0])
                else:
                    self.trigger_squeak_placement(
                        selected_squeak_id[0], selected_tiles[0].coord
                    )
            else:
                if selected_squeak_id:
                    self.return_squeak_to_hand(selected_squeaks[0])

            self._element_manager.deselect_all("SELECTMASK")
            self._element_manager.deselect_all("AVAILABLEMASK")

        self.camera.end_drag()

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

    def get_selected_tiles(self) -> list[Tile]:
        tiles = []
        tile_masks = self._element_manager.get_selected_elements("SELECTMASK")[1]
        for tile_elem in tile_masks:
            tiles.append(tile_elem.get_payload(TilePayload).tile)
        return tiles

    def get_available_tiles(self) -> list[Tile]:
        tiles = []
        tile_mask_elements = self._element_manager.get_selected_elements(
            "AVAILABLEMASK"
        )[1]
        for tile_elem in tile_mask_elements:
            tiles.append(tile_elem.get_payload(TilePayload).tile)
        return tiles

    def get_hover_tiles(self) -> list[Tile]:
        tiles = []
        tile_mask_elements = self._element_manager.get_selected_elements("HOVERMASK")[1]
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
        self.coordination_manager.put_message(
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

    def _close_ability_menu(self) -> None:
        """Close the ability menu if open."""
        if self.ability_panel_id:
            self._element_manager.remove_element(self.ability_panel_id)
            self.ability_panel_id = None

    def try_movement(self) -> None:
        """Triggers when the player selects an entity before selecting a tile."""

    def _get_ability_id(self, msg: pygame.event.Event) -> int:
        element_id = get_id(msg)
        if not element_id:
            raise ValueError(
                "Wrong event type received. Make sure it is a gesture type event!"
            )
        ability_button_elem_id = self.get_leaf_object_id(element_id)
        if ability_button_elem_id:
            return int(ability_button_elem_id.split("_")[1])
        else:
            raise ValueError("Ability button elem id is None.")

    # endregion

    # endregion
