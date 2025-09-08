import pygame_gui
import pygame
from typing import List

from .page_config import PAGES, PageConfig
from ratroyale.event_tokens import InputEvent
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.input.constants import PageName
from ratroyale.input.page.interactable import Interactable, TileInteractable, EntityInteractable
from ratroyale.event_tokens import GestureData
from ratroyale.visual.visual_component import VisualComponent
from ratroyale.backend.tile import Tile
from ratroyale.backend.entity import Entity
from ratroyale.backend.board import Board
from ratroyale.backend.hexagon import OddRCoord


# ============================================
# region Base Page Class
# ============================================

class Page:
    """Base class for a page in the application."""
    def __init__(self, page_name: PageName, screen_size: tuple[int, int], coordination_manager: CoordinationManager):
        self.config: PageConfig = PAGES[page_name]

        # Page name
        self.name: PageName = self.config.name

        # Canvas for free drawing (transparent)
        self.canvas = pygame.Surface(screen_size, pygame.SRCALPHA)

        # Each page has its own UIManager
        self.gui_manager = pygame_gui.UIManager(screen_size, self.config.theme_path)

        # Coordination manager to put events into.
        self.coordination_manager = coordination_manager

        # Registry for interactables (UI elements, tiles, cards, etc.)
        self.interactables: List[Interactable] = []

        # Registry for visual elements
        self.visuals: List[VisualComponent] = []

        for widget_config in self.config.widgets:
            visual_instances: list[VisualComponent] = []

            # Lazily create visuals if any exist
            for visual_cfg in getattr(widget_config, "visuals", []):
                # If the visual is a UIVisual, pass gui_manager; otherwise creation may be no-op
                visual_cfg.create(manager=self.gui_manager)
                visual_instances.append(visual_cfg)
                self.visuals.append(visual_cfg)

            # Create the Interactable with a list of visuals
            interactable_instance = Interactable(
                hitbox=widget_config.hitbox,
                gesture_action_mapping=widget_config.gesture_action_mapping,
                visuals=visual_instances,
                blocks_input=widget_config.blocks_input,
                z_order=getattr(widget_config, "z_order", 0)
            )

            self.add_element(interactable_instance)

        # Sort all interactables by Z-order (highest first)
        self.interactables.sort(key=lambda e: e.z_order, reverse=True)

        # Blocking flag: prevents input from reaching lower pages in the stack
        self.blocking = self.config.blocking

    def add_element(self, element: Interactable):
        self.interactables.append(element)

    def remove_element(self, element: Interactable):
        if element in self.interactables:
            self.interactables.remove(element)


    def handle_gestures(self, gestures: list[GestureData]):
        for gesture in gestures:
            for widget in self.interactables:
                action_key = widget.process_gesture(gesture)
                if action_key:
                    self.emit_input_event(InputEvent(
                        gesture_data=gesture,
                        action_key=action_key,
                        page_name=self.name
                    ))

                    if widget.blocks_input:
                        break  # stop here if widget consumes the gesture
        
    def emit_input_event(self, input_event: InputEvent):
        self.coordination_manager.input_domain_mailbox.put(input_event)


    def clear_canvas(self, color=(0, 0, 0, 0)):
        """Clear the canvas (default: fully transparent)."""
        self.canvas.fill(color)

    def update_ui(self, dt: float):
        """Update UI elements for animations, transitions, etc."""
        self.gui_manager.update(dt)

    def draw_ui(self):
        """Draw UI elements onto the page canvas."""
        self.gui_manager.draw_ui(self.canvas)

    def draw(self):
        pass

# endregion

# ====================================
# region Special Page Definitions
# ====================================

class GameBoardPage(Page):
    def __init__(self, screen_size: tuple[int,int],
                 coordination_manager: CoordinationManager, 
                 board: Board | None):
        super().__init__(PageName.GAME_BOARD, screen_size, coordination_manager)

        # Visuals for tiles and entities.
        self.tile_visuals: list[VisualComponent] = []
        self.entity_visuals: list[VisualComponent] = []

        # Visual-only selection and preview
        self.selected_unit: Interactable | None = None
        self.path_preview: list[Interactable] = []

        if board:
            for tile_list in board.tiles:
                for tile in tile_list:
                    tile_interactable = TileInteractable(tile)
                    self.add_element(tile_interactable)
                    self.tile_visuals.extend(tile_interactable.visuals)  
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
                    self.tile_visuals.extend(tile_interactable.visuals)

        # --- Entities as interactables ---
        # Kept in case we wanna test maps with entities already on.
        # for entity in entities:
        #     entity_interactable = EntityInteractable(entity)
        #     self.add_element(entity_interactable)
        #     self.entity_visuals.extend(entity_interactable.visuals)  # append to base class visuals
        #     print(entity_interactable)

        # Sort all interactables by Z-order (highest first)
        self.interactables.sort(key=lambda e: e.z_order, reverse=True)


    def draw(self):
        self.clear_canvas()  # optional: clear to transparent or a background color
        
        # Draw tiles first
        for tile in self.tile_visuals:
            tile.render(self.canvas)

        # Draw entities on top of tiles
        for entity in self.entity_visuals:
            entity.render(self.canvas)

        # Draw selection/path previews
        if self.selected_unit:
            # draw selection highlight
            pass
        if self.path_preview:
            for tile in self.path_preview:
                # draw path overlay
                pass

        self.render_hitbox()

        # Draw UI elements last
        self.draw_ui()

    # Hitbox debug
    def render_hitbox(self):
        for interactable in self.interactables:
            interactable.hitbox.draw(self.canvas)

class CardOverlayPage(Page):
    pass


# ====================================
# region Page Factory 
# ====================================

class PageFactory:
    def __init__(self, gui_manager, screen_size, coordination_manager: CoordinationManager):
        self.gui_manager = gui_manager
        self.screen_size = screen_size
        self.coordination_manager = coordination_manager

    # Used for creating non-specialized page classes.
    def create_page(self, page_option: PageName):
        return Page(page_option, self.screen_size, self.coordination_manager)
    
    def create_game_board_page(self, board: Board | None):
        return GameBoardPage(self.screen_size, self.coordination_manager, board)


    
# endregion
