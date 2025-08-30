import pygame_gui
import pygame
from pygame_gui.core.ui_element import UIElement
from .page_config_options import PageConfigOptions
from typing import List, Callable

class Page:
    """Base class for a page in the application."""
    def __init__(self, config: PageConfigOptions, screen_size: tuple[int, int]):
        # Defines the page name
        self.name = config.value["name"]

        # Canvas for this page (transparent by default)
        self.canvas = pygame.Surface(screen_size, pygame.SRCALPHA)

        # Each page has its own UIManager
        self.gui_manager = pygame_gui.UIManager(screen_size, config.value["theme_path"])

        # UI elements and callbacks
        self.elements = [
            widget_def["type"](manager=self.gui_manager, **widget_def["kwargs"])
            for widget_def in config.value["widgets"]
        ]
        # self.callbacks: dict[UIElement, Callable] = {}

        # Blocking flag: if true, blocks input from reaching lower pages in the stack.
        self.blocking = config.value["blocking"]

    # -----------------------
    # UI Element Management
    # -----------------------
    def add_element(self, element: UIElement, callback: Callable | None = None):
        self.elements.append(element)
        # if callback:
        #     self.callbacks[element] = callback

    def remove_element(self, element: UIElement):
        if element in self.elements:
            self.elements.remove(element)
        # if element in self.callbacks:
        #     del self.callbacks[element]

    def get_elements(self):
        return self.elements

    # -----------------------
    # Visibility
    # -----------------------
    def show(self):
        for element in self.elements:
            element.show()

    def hide(self):
        for element in self.elements:
            element.hide()

    # -----------------------
    # Event Handling
    # -----------------------
    def handle_events(self, events: list[pygame.event.Event]) -> list[pygame.event.Event]:
        unconsumed = []

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            consumed = False

            # First let UI elements consume the event
            for element in self.elements:
                if element.visible and element.process_event(event):
                    consumed = True
                    break

            # Then this page-specific logic
            # if not consumed and self.consume_event_logic(event):
            #     consumed = True

            # Keep unconsumed events for the next page
            if not consumed:
                unconsumed.append(event)

        return unconsumed

    # -----------------------
    # Callbacks
    # -----------------------
    # def get_callback(self, element: UIElement):
    #     return self.callbacks.get(element)

    # -----------------------
    # Canvas
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
