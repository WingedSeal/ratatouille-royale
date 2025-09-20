import pygame_gui
import pygame

from .page_config import PAGES, PageConfig
from ratroyale.event_tokens.input_token import InputManagerEvent, GestureData
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.input.page_management.page_name import PageName
from ratroyale.input.page_management.interactable import Interactable, TileInteractable, EntityInteractable
from ratroyale.visual.asset_management.visual_component import VisualComponent
from ratroyale.backend.tile import Tile
from ratroyale.backend.board import Board
from ratroyale.backend.hexagon import OddRCoord


# ============================================
# region Base Page Class
# ============================================

class Page:
    """Base class for a page in the application."""
    def __init__(self, page_name: PageName, screen_size: tuple[int, int], coordination_manager: CoordinationManager) -> None:
        self.config: PageConfig = PAGES[page_name]
        self.name: PageName = self.config.name

        self.canvas = pygame.Surface(screen_size, pygame.SRCALPHA)
        """ Canvas for blitting visual objects onto (transparent by default) """

        self.gui_manager = pygame_gui.UIManager(screen_size, self.config.theme_path)
        """ Each page has its own UIManager """

        self.coordination_manager = coordination_manager

        self.interactables: list[Interactable] = []
        """ Registry for interactables (UI elements, tiles, cards, etc.) """

        # self.visuals: list[VisualComponent] = []
        """ Registry for visual elements """

        for widget_config in self.config.widgets:
            # visual_instances: list[VisualComponent] = []

            # # For each widget, see if it has any visual components it'd like to create.
            # if widget_config.visuals:
            #     for visual_config in widget_config.visuals:
            #         # If it is of type UIVisual (e.g. buttons), pass in gui_manager to handle creation.
            #         # Otherwise, if it is of type SpriteVisual, the passed in gui_manager does nothing.
            #         visual_config.create(manager=self.gui_manager)
            #         visual_instances.append(visual_config)
            #         self.visuals.append(visual_config)

            # Then, create the interactable, and attach the visual components to it.
            # TODO: may separate the hitbox component and visual component in the future, to loosen
            # the coupling.
            interactable_instance = Interactable(
                hitbox=widget_config.hitbox,
                gesture_action_mapping=widget_config.gesture_action_mapping,
                # visuals=visual_instances,
                blocks_input=widget_config.blocks_input,
                z_order=widget_config.z_order
            )

            self.add_element(interactable_instance)

        self.interactables.sort(key=lambda e: e.z_order, reverse=True)

        # Blocking flag: prevents input from reaching lower pages in the stack
        self.blocking = self.config.blocking

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
                    self.emit_input_event(InputManagerEvent(
                        gesture_data=gesture,
                        action_key=action_key,
                        interactable=interactable
                    ))

                    if interactable.blocks_input:
                        break
            else:
                remaining_gestures.append(gesture)

        return remaining_gestures

        
    def emit_input_event(self, input_event: InputManagerEvent) -> None:
        self.coordination_manager.put_message(input_event)


    def clear_canvas(self, color: tuple[int, int, int, int]=(0, 0, 0, 0)) -> None:
        """Clear the canvas (default: fully transparent)."""
        self.canvas.fill(color)

    def update_ui(self, dt: float) -> None:
        """Update UI elements for animations, transitions, etc."""
        self.gui_manager.update(dt)

    def draw_ui(self) -> None:
        """Draw UI elements onto the page canvas."""
        self.gui_manager.draw_ui(self.canvas)

    def draw(self) -> None:
        """Draw method for non-UI elements. Used as a base to be extended by special page definitions."""
        pass

# endregion

# ====================================
# region Special Page Definitions
# ====================================

class GameBoardPage(Page):
    def __init__(self, screen_size: tuple[int,int],
                 coordination_manager: CoordinationManager, 
                 board: Board | None) -> None:
        super().__init__(PageName.GAME_BOARD, screen_size, coordination_manager)

        # self.tile_visuals: list[VisualComponent] = []
        # """ Visual components for tiles """
        # self.entity_visuals: list[VisualComponent] = []
        # """ Visual components for entities """

        self.selected_unit: Interactable | None = None
        """ Keeps track of which unit is being selected """
        self.path_preview: list[Interactable] = []
        """ Keeps track of tiles included in path dragging """

        if board:
            for tile_list in board.tiles:
                for tile in tile_list:
                    if tile:
                        tile_interactable = TileInteractable(tile)
                        self.add_element(tile_interactable)
                        # self.tile_visuals.extend(tile_interactable.visuals)
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
                    # self.tile_visuals.extend(tile_interactable.visuals)

        # --- Entities as interactables ---
        # Iterate over all entities on the board (or empty list if no board)
        entities_to_add = board.cache.entities if board else []
        for entity in entities_to_add:
            entity_interactable = EntityInteractable(entity)
            self.add_element(entity_interactable)
            # self.entity_visuals.extend(entity_interactable.visuals)

        # Sort all interactables by Z-order (highest first)
        self.interactables.sort(key=lambda e: e.z_order, reverse=True)


    # def draw(self) -> None:
    #     self.clear_canvas()  
        
    #     # TODO: Revise the draw order to align with the isometric style.

    #     for tile in self.tile_visuals:
    #         tile.render(self.canvas)

    #     for entity in self.entity_visuals:
    #         entity.render(self.canvas)

    #     # TODO: implement unit selection & path preview highlight.
    #     # if self.selected_unit:
    #     #     pass
    #     # if self.path_preview:
    #     #     for tile in self.path_preview:
    #     #         pass

    #     # TODO: implement SHOW HITBOX trigger
    #     self.render_hitbox()

    #     # Draw UI elements last
    #     self.draw_ui()

    # # Hitbox debug
    # def render_hitbox(self) -> None:
    #     for interactable in self.interactables:
    #         interactable.hitbox.draw(self.canvas)

class CardOverlayPage(Page):
    pass

