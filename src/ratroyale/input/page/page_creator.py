import pygame_gui
import pygame
from pygame_gui.core.ui_element import UIElement
from typing import Callable

from .page_config import PAGES, PageConfig
from ratroyale.input.page.gesture_reader import GestureReader
from ratroyale.event_tokens import InputEvent
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.input.constants import GUIEventSource, PageName, CONSUMED_UI_EVENTS, UI_WIDGETS_ALWAYS_CONSUMING
from ratroyale.input.page.wrapped_widgets import WrappedWidget


class Page:
    """Base class for a page in the application."""
    def __init__(self, page_name: PageName, screen_size: tuple[int, int], coordination_manager: CoordinationManager):
        self.config: PageConfig = PAGES[page_name]

        # Strongly typed page name
        self.name: PageName = self.config.name

        # Canvas for free drawing (transparent)
        self.canvas = pygame.Surface(screen_size, pygame.SRCALPHA)

        # Each page has its own UIManager
        self.gui_manager = pygame_gui.UIManager(screen_size, self.config.theme_path)

        # GUI callback queue for navigation
        self.gui_callback_queue = coordination_manager

        # Gesture handling for this page
        self.gesture_reader = GestureReader(self.name, coordination_manager)

        # Registry for wrapped UI elements
        self.elements: list[WrappedWidget] = []
        self.callbacks: dict[WrappedWidget, Callable] = {}

        for widget_config in self.config.widgets:
            # Instantiate the wrapped widget
            widget_instance = widget_config.type(manager=self.gui_manager, blocks_input=widget_config.blocks_input,**widget_config.kwargs)

            # Add widget to page and register callback
            self.add_element(
                widget_instance,
                callback=lambda key=widget_config.action_key: coordination_manager.put_message(
                    InputEvent(
                        source=GUIEventSource.UI_ELEMENT,
                        action_key=key,
                        page_name=self.name
                    )
                )
            )

        # Blocking flag: prevents input from reaching lower pages in the stack
        self.blocking = self.config.blocking


    # -----------------------
    # region UI Element Management
    # -----------------------
    def add_element(self, element: WrappedWidget, callback: Callable | None = None):
        self.elements.append(element)
        if callback:
            self.callbacks[element] = callback

    def remove_element(self, element: UIElement):
        if element in self.elements:
            self.elements.remove(element)
    
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

    def handle_events(self, events: list[pygame.event.Event]) -> list[pygame.event.Event]:
        unconsumed = []

        for event in events:
            # Always handle quit immediately
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            over_ui = False  # Flag for whether this event intersects a blocking widget

            # First, let each wrapped widget process the event
            for wrapped_widget in self.elements:
                wrapped_widget.handle_event(event)

                # Trigger callback if this is a button press for this wrapped widget
                if event.type == pygame_gui.UI_BUTTON_PRESSED and getattr(event, "ui_element", None) == getattr(wrapped_widget, "button", None):
                    callback = self.callbacks.get(wrapped_widget)
                    if callback:
                        callback()

                # If event interacts with the widget and blocks input, mark it
                panel_rect = wrapped_widget.panel.get_relative_rect()
                if wrapped_widget.blocks_input and panel_rect.collidepoint(pygame.mouse.get_pos()):
                    over_ui = True

            # Always let UIManager process hover/focus for visual feedback
            self.gui_manager.process_events(event)

            # Only pass event to canvas/gesture reader if it’s not blocked
            if not over_ui:
                unconsumed.append(event)

        # Pass unconsumed events to the gesture reader with a flag
        self.gesture_reader.handle_events(unconsumed, blocked=over_ui)

        return unconsumed

    
    def hovering_ui(self, event: pygame.event.Event):
        if event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
            return True
        elif event.type == pygame_gui.UI_BUTTON_ON_UNHOVERED:
            return False
    
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
