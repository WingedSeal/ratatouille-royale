import pygame_gui
import pygame
from pygame_gui.elements import UIPanel
from typing import List, Callable


"""Base class for a page in the application."""
class Page:
    def __init__(self, name: str, gui_manager: pygame_gui.UIManager, container_rect: pygame.Rect):
        self.name = name
        self.container = UIPanel(relative_rect=container_rect, manager=gui_manager)
        self.elements: List[pygame_gui.elements.UIElement] = []  # List of UI elements on this page
        self.callbacks: dict[pygame_gui.elements.UIElement, callable] = {} # List of callbacks for elements

        self.container.hide()

    def add_element(self, element, callback: Callable = None):
        # Attach element to container
        element.set_container(self.container)
        self.elements.append(element)
        if callback:
            self.callbacks[element] = callback

    def remove_element(self, element):
        self.elements.remove(element)

    def get_elements(self):
        return self.elements
    
    def hide(self):
        self.container.hide()

    def show(self):
        self.container.show()
    
    def handle_events(self, events):
        """Process events for all elements on this page."""
        for event in events:
            for element in self.elements:
                # pygame_gui already handles event routing via UIManager
                # this is for placeholder if custom handling is needed
                pass

    def get_callback(self, element):
        return self.callbacks.get(element)
    
    def resize(self, new_rect: pygame.Rect):
        """Resize container and optionally adjust children positions"""
        self.container.set_relative_rect(new_rect)

        # Optional: reposition child elements proportionally
        for element in self.elements:
            rel_x = element.relative_rect.x / self.container.relative_rect.width
            rel_y = element.relative_rect.y / self.container.relative_rect.height
            element_width = element.relative_rect.width
            element_height = element.relative_rect.height
            element.set_relative_position((rel_x * new_rect.width, rel_y * new_rect.height))
            # Optionally scale element size too
            element.set_dimensions((element_width, element_height))