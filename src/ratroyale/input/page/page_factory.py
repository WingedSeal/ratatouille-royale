import pygame_gui
import pygame
from pygame_gui.core.ui_element import UIElement
from typing import Callable

from .page_config import PAGES, PageConfig
from ratroyale.input.page.gesture_reader import GestureReader
from ratroyale.event_tokens import InputEvent
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.input.constants import GUIEventSource, PageName, CONSUMED_UI_EVENTS, UI_WIDGETS_ALWAYS_CONSUMING


class Page:
    """Base class for a page in the application."""
    def __init__(self, page_name: PageName, screen_size: tuple[int, int], coordination_manager: CoordinationManager):
        self.config: PageConfig = PAGES[page_name]

        # Defines the page name (strongly typed)
        self.name: PageName = self.config.name

        # Canvas for this page (transparent by default)
        self.canvas = pygame.Surface(screen_size, pygame.SRCALPHA)

        # Each page has its own UIManager
        self.gui_manager = pygame_gui.UIManager(screen_size, self.config.theme_path)

        # GUI callback queue for navigation
        self.gui_callback_queue = coordination_manager

        # Each page also has its own GestureReader
        self.gesture_reader = GestureReader(self.name, coordination_manager)

        # UI elements and callbacks
        self.callbacks: dict[pygame_gui.core.UIElement, Callable] = {}
        self.elements: list[pygame_gui.core.UIElement] = []

        for widget in self.config.widgets:
            element = widget.type(manager=self.gui_manager, **widget.kwargs)
            self.add_element(
                element,
                callback=lambda key=widget.action_key: coordination_manager.put_message(
                    InputEvent(
                        source=GUIEventSource.UI_ELEMENT,
                        action_key=key,
                        page_name=self.name
                    )
                )
            )
        
        # Blocking flag: if true, blocks input from reaching lower pages in the stack.
        self.blocking = self.config.blocking

    # -----------------------
    # region UI Element Management
    # -----------------------
    def add_element(self, element: UIElement, callback: Callable | None = None):
        self.elements.append(element)
        if callback:
            self.callbacks[element] = callback

    def remove_element(self, element: UIElement):
        if element in self.elements:
            self.elements.remove(element)
        # if element in self.callbacks:
        #     del self.callbacks[element]

    def get_elements(self):
        return self.elements
    
    # endregion

    # -----------------------
    # region Visibility
    # -----------------------
    def show(self):
        for element in self.elements:
            element.show()

    def hide(self):
        for element in self.elements:
            element.hide()

    # endregion

    # -----------------------
    # region Event Handling
    # -----------------------

    # FIXME: input filtering for gesture not working.
    # FIXME: possibly needs to extend pygame_gui's components for custom behavior.
    def handle_events(self, events: list[pygame.event.Event]) -> list[pygame.event.Event]:
        unconsumed = []

        for event in events:
            # Always handle quit immediately
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # Let UIManager process the event
            consumed_by_gui = self.gui_manager.process_events(event)

            # Determine if the event should be fully consumed
            consumed = False
            if consumed_by_gui:
                # Only consume if the event came from certain widgets
                if hasattr(event, "ui_element") and isinstance(event.ui_element, UI_WIDGETS_ALWAYS_CONSUMING):
                    consumed = True

            # Consume GUI-specific events regardless of widget
            if event.type in CONSUMED_UI_EVENTS:
                consumed = True

            # Execute any callbacks for buttons
            if event.type == pygame_gui.UI_BUTTON_PRESSED and hasattr(event, "ui_element"):
                callback = self.callbacks.get(event.ui_element)
                if callback:
                    callback()

            # If no UI widgets consume the event, but the UI widgets are hovered on,
            # consider the event consumed anyways.
            consumed = self.hovering_ui(event) or consumed

            # If not consumed, keep for game/input logic
            if not consumed:
                unconsumed.append(event)

        # Let gesture reader handle all events
        self.gesture_reader.handle_events(unconsumed)

        return unconsumed
    
    def hovering_ui(self, event: pygame.event.Event):
        if event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
            return True
        elif event.type == pygame_gui.UI_BUTTON_ON_UNHOVERED:
            return False
    
    # endregion

    # -----------------------
    # region Callbacks
    # -----------------------
    def get_callback(self, element: UIElement):
        return self.callbacks.get(element)
    
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
