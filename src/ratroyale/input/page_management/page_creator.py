import pygame_gui

from .page_config import PAGES, PageConfig
from ratroyale.event_tokens.input_token import InputManagerEvent, GestureData
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.input.page_management.page_name import PageName
from ratroyale.input.interactables_management.interactable import Interactable, TileInteractable, EntityInteractable
from ratroyale.visual.asset_management.visual_component import VisualComponent
from ratroyale.backend.tile import Tile
from ratroyale.backend.board import Board
from ratroyale.backend.hexagon import OddRCoord
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *
from ratroyale.visual.asset_management.visual_component import EntityVisual, TileVisual, TYPICAL_TILE_SIZE
from ratroyale.backend.entity import Entity
from ratroyale.visual.screen_constants import SCREEN_SIZE


# ============================================
# region Base Page Class
# ============================================

class Page:
    """Base class for a page in the application."""
    def __init__(self, page_name: PageName, coordination_manager: CoordinationManager) -> None:
        self.config: PageConfig = PAGES[page_name]
        self.name: PageName = self.config.name
        self.screen_size: tuple[int, int] = SCREEN_SIZE

        gui_manager = pygame_gui.UIManager(SCREEN_SIZE, self.config.theme_path)
        """ Each page has its own UIManager """

        self.coordination_manager = coordination_manager

        self._register_self(gui_manager)

        self.interactables: list[Interactable] = []
        """ Registry for interactables (UI elements, tiles, cards, etc.) """

        for widget_config in self.config.widgets:
            visual_instances: list[VisualComponent] = []

            # Then, create the interactable, and attach the visual components to it.
            interactable_instance = Interactable(
                hitbox=widget_config.hitbox,
                gesture_action_mapping=widget_config.gesture_action_mapping,
                blocks_input=widget_config.blocks_input,
                z_order=widget_config.z_order
            )
            self.add_element(interactable_instance)

            # For each widget, see if it has any visual components it'd like to create.
            if widget_config.visuals:
                for visual_config in widget_config.visuals:
                    # If it is of type UIVisual (e.g. buttons), pass in gui_manager to handle creation.
                    # Otherwise, if it is of type SpriteVisual, the passed in gui_manager does nothing.
                    visual_config.create(manager=gui_manager)
                    visual_instances.append(visual_config)
                    coordination_manager.put_message(
                        RegisterVisualComponent_VisualManagerEvent(
                            self.name,
                            visual_instances, 
                            interactable_instance,
                            ))

        self.interactables.sort(key=lambda e: e.z_order, reverse=True)

        # Blocking flag: prevents input from reaching lower pages in the stack
        self.blocking = self.config.blocking

    def _register_self(self, ui_manager: pygame_gui.UIManager) -> None:
        self.coordination_manager.put_message(RegisterPage_VisualManagerEvent(self.name, ui_manager))

    def _unregister_self(self) -> None:
        self.coordination_manager.put_message(UnregisterPage_VisualManagerEvent(self.name))

    def add_element(self, element: Interactable) -> None:
        self.interactables.append(element)

    def remove_element(self, element: Interactable) -> None:
        if element in self.interactables:
            self.interactables.remove(element)

    def handle_gestures(self, gestures: list[GestureData]) -> list[GestureData]:
        remaining_gestures: list[GestureData] = []

        for gesture in gestures:
            for interactable in self.interactables:
                action_key = interactable.process_gesture(gesture)
                if action_key:
                    self.coordination_manager.put_message(InputManagerEvent(
                        gesture_data=gesture,
                        action_key=action_key,
                        interactable=interactable,
                        page_name=self.name
                    ))

                    if interactable.blocks_input:
                        break
            else:
                remaining_gestures.append(gesture)

        return remaining_gestures
    
    def execute_callback(self, tkn: PageManagerEvent) -> None:
        pass

# endregion

# ====================================
# region Special Page Definitions
# ====================================

# TODO: delegate visual component creation to a factory
# TODO: create method to delete element
class GameBoardPage(Page):
    def __init__(self,
                 coordination_manager: CoordinationManager, 
                 board: Board | None) -> None:
        super().__init__(PageName.GAME_BOARD, coordination_manager)

        self.tile_interactables: dict[OddRCoord, TileInteractable] = {}
        self.entity_interactables: dict[Entity, EntityInteractable] = {}

        self.selected_entity: Entity | None = None
        self.selected_tile: OddRCoord | None = None

        if board:
            for tile_list in board.tiles:
                for tile in tile_list:
                    if tile:
                        tile_interactable = TileInteractable(tile)
                        self.add_element(tile_interactable)

                        coordination_manager.put_message(
                            RegisterVisualComponent_VisualManagerEvent(
                                visual_component=[TileVisual(tile)],
                                interactable=tile_interactable,
                                page_name=self.name
                            )
                        )
        else:
            # Create a 5x5 grid of Tiles
            for q in range(5):
                for r in range(5):
                    tile = Tile(
                        coord=OddRCoord(q, r),
                        entities=[],
                        height=0,
                        features=[]
                    )
                    tile_interactable = TileInteractable(tile)
                    self.add_element(tile_interactable)

                    coordination_manager.put_message(
                            RegisterVisualComponent_VisualManagerEvent(
                                visual_component=[TileVisual(tile)],
                                interactable=tile_interactable,
                                page_name=self.name
                            )
                        )

        # --- Entities as interactables ---
        # Iterate over all entities on the board (or empty list if no board)
        entities_to_add = board.cache.entities if board else []
        for entity in entities_to_add:
            entity_interactable = EntityInteractable(entity)
            self.add_element(entity_interactable)

            coordination_manager.put_message(
                            RegisterVisualComponent_VisualManagerEvent(
                                page_name=self.name,
                                visual_component=[EntityVisual(entity)],
                                interactable=entity_interactable
                            )
                        )

        # Sort all interactables by Z-order (highest first)
        self.interactables.sort(key=lambda e: e.z_order, reverse=True)

        print(len(self.tile_interactables.values()))

    def add_element(self, element: Interactable) -> None:
        super().add_element(element)

        match element:
            case TileInteractable():
                self.tile_interactables[element.tile.coord] = element
            case EntityInteractable():
                self.entity_interactables[element.entity] = element

    def execute_callback(self, tkn: PageManagerEvent) -> None:
        super().execute_callback(tkn)

        match tkn:
            case EntityInteraction_PageManagerEvent(entity=e):
                self._select_entity(e)
            case TileInteraction_PageManagerEvent(tile=t):
                self._select_tile(t)
                self._try_entity_movement(t)
            case EntityMovementConfirmation_PageManagerEvent(success=s, error_msg=e):
                self._move_entity(s, e)
            case _:
                pass

    def _select_entity(self, entity: Entity) -> None:
        self.selected_entity = entity if entity is not self.selected_entity else None

    def _select_tile(self, tile: Tile) -> None:
        self.selected_tile = tile.coord if tile.coord is not self.selected_tile else None

    def _try_entity_movement(self, tile: Tile) -> None:
        if self.selected_entity:
            self.coordination_manager.put_message(RequestEntityMovement_GameManagerEvent(self.name, self.selected_entity, tile))

    def _move_entity(self, success: bool, error_msg: str | None) -> None:
        if success and self.selected_entity is not None and self.selected_tile is not None:
            entity = self.entity_interactables.get(self.selected_entity)
            if entity:
                coord = self._calculate_new_position(self.selected_tile)

                entity.hitbox.move_to(coord)
                self.coordination_manager.put_message(EntityMovementConfirmation_VisualManagerEvent(self.name, success, error_msg, coord))

                self._clear_selection()
        else:
            print(error_msg)

    def _calculate_new_position(self, coord: OddRCoord) -> tuple[float, float]:
        x, y = coord.to_pixel(*TYPICAL_TILE_SIZE, is_bounding_box=True)
        return (x, y)
    
    def _clear_selection(self):
        self.selected_tile = None
        self.selected_entity = None

class CardOverlayPage(Page):
    pass

