import pygame_gui
import pygame
from pygame_gui.core.ui_element import UIElement
from typing import List

from .page_config import PAGES, PageConfig
from ratroyale.event_tokens import InputEvent
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.input.constants import PageName, CONSUMED_UI_EVENTS
from ratroyale.input.page.interactable import Interactable
from ratroyale.event_tokens import GestureData
from ratroyale.visual.visual_component import VisualComponent


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

        # Registry for interactable UI elements
        self.elements: List[Interactable] = []

        for widget_config in self.config.widgets:
            visual_instances: list[VisualComponent] = []

            # Lazily create visuals if any exist
            for visual_cfg in getattr(widget_config, "visuals", []):
                # If the visual is a UIVisual, pass gui_manager; otherwise creation may be no-op
                visual_cfg.create(manager=self.gui_manager)
                visual_instances.append(visual_cfg)

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
        self.elements.sort(key=lambda e: e.z_order, reverse=True)

        # Blocking flag: prevents input from reaching lower pages in the stack
        self.blocking = self.config.blocking


    # -----------------------
    # region UI Element Management
    # -----------------------
    def add_element(self, element: Interactable):
        self.elements.append(element)

    def remove_element(self, element: Interactable):
        if element in self.elements:
            self.elements.remove(element)
    
    # endregion

    # -----------------------
    # region Event Handling
    # -----------------------

    def handle_gestures(self, gestures: list[GestureData]):
        for gesture in gestures:
            for widget in self.elements:
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

    # endregion

    # -----------------------
    # region Canvas
    # -----------------------
    def clear_canvas(self, color=(0, 0, 0, 0)):
        """Clear the canvas (default: fully transparent)."""
        self.canvas.fill(color)

    def update_ui(self, dt: float):
        """Update UI elements for animations, transitions, etc."""
        self.gui_manager.update(dt)

    def draw_ui(self):
        """Draw UI elements onto the page canvas."""
        self.gui_manager.draw_ui(self.canvas)

    # endregion

"""
    ACCOMPANYING PAGE FACTORY CLASS
"""

class PageFactory:
    def __init__(self, gui_manager, screen_size, coordination_manager: CoordinationManager):
        self.gui_manager = gui_manager
        self.screen_size = screen_size
        self.gui_callback_queue = coordination_manager

    def create_page(self, page_option: PageName):
        return Page(page_option, self.screen_size, self.gui_callback_queue)
