import pygame_gui
from typing import List

"""Base class for a page in the application."""
class Page:
    def __init__(self, name):
        self.name = name
        self.elements: List[pygame_gui.elements.UIElement] = []  # List of UI elements on this page
        self.callbacks: dict[pygame_gui.elements.UIElement, callable] = {} # List of callbacks for elements

    def add_element(self, element, callback=None):
        self.elements.append(element)
        if callback:
            self.callbacks[element] = callback

    def remove_element(self, element):
        self.elements.remove(element)

    def get_elements(self):
        return self.elements
    
    def handle_events(self, events):
        """Process events for all elements on this page."""
        for event in events:
            for element in self.elements:
                # pygame_gui already handles event routing via UIManager
                # this is for placeholder if custom handling is needed
                pass