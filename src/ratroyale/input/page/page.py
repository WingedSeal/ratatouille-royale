import pygame_gui
import pygame
from pygame_gui.core.ui_element import UIElement
from .page_config_options import PageConfigOptions
from typing import Callable
from ratroyale.utils import EventQueue
from ratroyale.input.gesture_reader import GestureReader
from ratroyale.input.event_token import InputEventToken, GUIEventSource
from ratroyale.input.coordination_manager import CoordinationManager

class Page:
    """Base class for a page in the application."""
    def __init__(self, config: PageConfigOptions, screen_size: tuple[int, int], coordination_manager: CoordinationManager):
        # Defines the page name
        self.name = config.value["name"]

        # Canvas for this page (transparent by default)
        self.canvas = pygame.Surface(screen_size, pygame.SRCALPHA)

        # Each page has its own UIManager
        self.gui_manager = pygame_gui.UIManager(screen_size, config.value["theme_path"])

        # Each page also has its own GestureReader
        self.gesture_reader = GestureReader(self.name, coordination_manager)

        # GUI callback queue for navigation
        self.gui_callback_queue = coordination_manager

        # UI elements and callbacks
        self.callbacks: dict[UIElement, Callable] = {}
        self.elements = []
        for widget in config.value["widgets"]:
            btn = widget["type"](manager=self.gui_manager, **widget["kwargs"])
            self.add_element(btn, callback=lambda key=widget["callback_key"]: coordination_manager.put_message(
                InputEventToken(
                    source=GUIEventSource.UI_ELEMENT,
                    id=key,
                    page=self.name
                )
            ))
        
        # Blocking flag: if true, blocks input from reaching lower pages in the stack.
        self.blocking = config.value["blocking"]

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
    def handle_events(self, events: list[pygame.event.Event]) -> list[pygame.event.Event]:
        unconsumed = []

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # Let the UIManager process the event
            self.gui_manager.process_events(event)

            # Check if a button was pressed
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element in self.callbacks:
                    # Execute the stored lambda
                    self.callbacks[event.ui_element]()

            # Check if this event should be considered unconsumed
            # (only if you want custom page logic to handle it)
            # Example:
            # if not self.consume_event_logic(event):
            #     unconsumed.append(event)

        return unconsumed
    
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
        self.page_option_menu: dict[str, PageConfigOptions] = {
            "MAIN_MENU": PageConfigOptions.MAIN_MENU,
            "TEST_SWAP": PageConfigOptions.TEST_SWAP,
            "BOARD": PageConfigOptions.BOARD
        }

    def create_page(self, page_option: str):
        return Page(self.page_option_menu[page_option], self.screen_size, self.gui_callback_queue)
