from __future__ import annotations
import pygame_gui
import pygame


from ratroyale.event_tokens.input_token import InputManagerEvent
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.frontend.pages.page_elements.element import Element
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *
from ratroyale.frontend.visual.screen_constants import SCREEN_SIZE, THEME_PATH
from typing import Callable
from ratroyale.frontend.gesture.gesture_data import GestureData, GestureType
from ratroyale.frontend.pages.page_elements.element_builder import create_element, ElementConfig
from ratroyale.frontend.pages.page_elements.element_manager import ElementManager
from ratroyale.event_tokens.game_action import GameAction


class Page():
    """Base class for a page in the application."""
    def __init__(self, coordination_manager: CoordinationManager, is_blocking: bool = True) -> None:
        self.gui_manager = pygame_gui.UIManager(SCREEN_SIZE, THEME_PATH)
        """ Each page has its own UIManager """
        self.coordination_manager = coordination_manager
        self.is_blocking: bool = is_blocking
        self._element_manager: ElementManager = ElementManager(self.gui_manager, self.coordination_manager)
        self.canvas = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
        self.is_visible: bool = True

        self._input_bindings: dict[tuple[str, GestureType], Callable] = {}
        """ Maps (interactable_id, gesture_type) to handler functions """
        self._page_bindings: dict[GameAction, Callable] = {}
        """ Maps (game_action) to handler functions """

        self.setup_input_bindings()

    def setup_elements(self, configs: list[ElementConfig]) -> None:
        self._element_manager.create_elements(configs)

    def setup_input_bindings(self) -> None:
        """
        Scan all methods of the page instance for `x_bindings` metadata
        and populate x_bindings dict.
        """
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr):
                if hasattr(attr, "input_bindings"):
                    for widget_id, gesture_type in attr.input_bindings:
                        self._input_bindings[(widget_id, gesture_type)] = attr
                if hasattr(attr, "page_bindings"):
                    print(attr.page_bindings)
                    for page_event in attr.page_bindings:
                        self._page_bindings[page_event] = attr

    def handle_inputs(self, gestures: list[GestureData]) -> list[GestureData]:
        """
        Dispatch a GestureData object to the appropriate Interactable(s).
        Interactable then produces the corresponding InputManagerEvent, which is
        handled by the page.
        If the page is hidden, it will not process any gestures.
        """
        if not self.is_visible:
            return gestures

        return self._element_manager.handle_inputs(gestures)

    def execute_input_callback(self, msg: InputManagerEvent) -> None:
        """
        Executes the callback associated with the given InputManagerEvent.
        """
        handler = self._input_bindings.get((msg.interactable_id, msg.gesture_data.gesture_type))
        if handler:
            handler(msg)
    
    def execute_page_callback(self, msg: PageQueryResponseEvent) -> None:
        """
        Executes the callback associated with the given PageQueryResponseEvent.
        """
        handler = self._page_bindings.get(msg.game_action)
        if handler:
            handler(msg)
    
    def execute_visual_callback(self, msg: VisualManagerEvent) -> None:
        pass
    
    def hide(self) -> None:
        self.is_visible = False

    def show(self) -> None:
        self.is_visible = True

    def on_create(self) -> None:
        """ Called when the page is created. Override in subclasses if needed. """
        pass

    def on_destroy(self) -> None:
        """ Called when the page is destroyed. Override in subclasses if needed. """
        pass

    def render(self, time_delta: float) -> pygame.Surface:
        if self.is_visible:
            self.gui_manager.update(time_delta)
            self.canvas.fill((0, 0, 0, 0))  # Clear with transparent
            self._element_manager.render_all(self.canvas)
            self.gui_manager.draw_ui(self.canvas)
            return self.canvas
        else:
            return pygame.Surface((0, 0))  