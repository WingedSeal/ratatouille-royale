import pygame_gui
import pygame
from pygame_gui.core.ui_element import UIElement
from typing import List

from .page_config import PAGES, PageConfig
from ratroyale.event_tokens import InputEvent
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.input.constants import PageName, CONSUMED_UI_EVENTS, UI_WIDGETS_ALWAYS_CONSUMING, ActionKey
from ratroyale.input.page.wrapped_widgets import WrappedWidget, WrappedButton
from ratroyale.event_tokens import GestureData


# TODO: Revise button creation.
# 
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

        # Coordination manager to put events into.
        self.coordination_manager = coordination_manager

        # Registry for wrapped UI elements
        # self.elements: list[WrappedWidget] = []
        # self.callbacks: dict[WrappedWidget, Callable] = {}

        # for widget_config in self.config.widgets:
        #     # Instantiate the wrapped widget
        #     widget_instance = widget_config.type(
        #         manager=self.gui_manager, 
        #         blocks_input=widget_config.blocks_input,
        #         **widget_config.kwargs)

        #     # Add widget to page and register callback
        #     self.add_element(
        #         widget_instance,
        #         callback=lambda key=widget_config.action_key: coordination_manager.put_message(
        #             InputEvent(
        #                 source=GUIEventSource.UI_ELEMENT,
        #                 action_key=key,
        #                 page_name=self.name
        #             )
        #         )
        #     )

        # Registry for wrapped UI elements
        self.elements: List[WrappedWidget] = []

        # HACK: make this cleaner later
        for widget_config in self.config.widgets:
            if issubclass(widget_config.type, WrappedButton):
                # Explicitly pass button_text for buttons
                widget_instance = widget_config.type(
                    manager=self.gui_manager,
                    rect=widget_config.rect,
                    gesture_action_mapping=widget_config.gesture_action_mapping,
                    blocks_input=widget_config.blocks_input,
                    button_text=widget_config.button_text
                )
            else:
                # Generic widgets
                widget_instance = widget_config.type(
                    manager=self.gui_manager,
                    rect=widget_config.rect,
                    gesture_action_mapping=widget_config.gesture_action_mapping,
                    blocks_input=widget_config.blocks_input
                )

            self.add_element(widget_instance)


        # Blocking flag: prevents input from reaching lower pages in the stack
        self.blocking = self.config.blocking


    # -----------------------
    # region UI Element Management
    # -----------------------
    def add_element(self, element: WrappedWidget):
        self.elements.append(element)

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

    def handle_gestures(self, gestures: list[GestureData]) -> list[GestureData]:
        """
        Process gestures for this page.
        Returns gestures that were not consumed by UI elements.
        """
        remaining_gestures = []

        for gesture in gestures:
            consumed = False

            # --- Tier 1: UI Elements ---
            for widget in self.elements:
                action_key = widget.process_gesture(gesture)
                if action_key:
                    # Emit an InputEvent to the page manager / pipeline
                    self.emit_input_event(InputEvent(
                        gesture_data=gesture,
                        action_key=action_key,
                        page_name=self.name
                    ))

                    consumed = True
                    if widget.blocks_input:
                        break  # stop propagating to other widgets

            # --- Tier 2: Canvas ---
            if not consumed:
                remaining_gestures.append(gesture)

        # Canvas can now process the remaining gestures
        for gesture in remaining_gestures:
            self.process_canvas_gesture(gesture)

        return remaining_gestures  # for external handling

    def hovering_ui(self, event: pygame.event.Event):
        if event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
            return True
        elif event.type == pygame_gui.UI_BUTTON_ON_UNHOVERED:
            return False
        
    def emit_input_event(self, input_event: InputEvent):
        print(input_event)
        self.coordination_manager.input_domain_mailbox.put(input_event)

    def process_canvas_gesture(self, gesture: GestureData):
        self.coordination_manager.input_domain_mailbox.put(
            InputEvent(
                gesture_data=gesture, 
                action_key=ActionKey.NON_UI, 
                page_name=self.name))

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
