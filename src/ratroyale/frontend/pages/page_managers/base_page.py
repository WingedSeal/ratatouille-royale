from __future__ import annotations
import pygame_gui
import pygame

from ratroyale.event_tokens.input_token import InputManagerEvent
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.frontend.pages.page_elements.element import Element
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *
from ratroyale.frontend.visual.screen_constants import SCREEN_SIZE
from typing import Callable
from ratroyale.frontend.gesture.gesture_data import GestureData, GestureType
from ratroyale.frontend.pages.page_elements.element_builder import create_element, ElementConfig, ElementType
from ratroyale.frontend.pages.page_elements.element_manager import ElementManager
from ratroyale.event_tokens.game_action import GameAction
from ratroyale.frontend.pages.page_managers.theme_path_helper import resolve_theme_path


class Page():
    """Base class for a page in the application."""
    def __init__(self, 
                 coordination_manager: CoordinationManager, 
                 is_blocking: bool = True, 
                 theme_name: str = "",
                 base_color: tuple[int, int, int, int]  | None = None) -> None:
        self.theme_path = str(resolve_theme_path(theme_name))
        self.gui_manager = pygame_gui.UIManager(SCREEN_SIZE, self.theme_path)
        """ Each page has its own UIManager """
        self.coordination_manager = coordination_manager
        self.is_blocking: bool = is_blocking
        self._element_manager: ElementManager = ElementManager(self.gui_manager, self.coordination_manager)
        self.canvas = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
        self.base_color: tuple[int, int, int, int] = base_color if base_color else (0, 0, 0, 0)
        self.is_visible: bool = True

        self._input_bindings: dict[tuple[str, GestureType], Callable] = {}
        """ Maps (interactable_id, gesture_type) to handler functions """
        self._page_bindings: dict[GameAction, Callable] = {}
        """ Maps (game_action) to handler functions """

        self.setup_input_bindings()

    def setup_elements(self, configs: list[ElementConfig]) -> None:
        self._element_manager.create_elements(configs)

    def get_element(self, element_type: ElementType, element_id: str) -> Element | None:
        return self._element_manager.get_element(element_type, element_id)

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

    def execute_input_callback(self, msg: InputManagerEvent) -> bool:
        """
        Executes the callback associated with the given InputManagerEvent.
        Supports prefix matching for element IDs.
        """
        for (prefix, gesture_type), handler in self._input_bindings.items():
            if gesture_type == msg.gesture_data.gesture_type and (
                msg.element_id == prefix or msg.element_id.startswith(prefix)
            ):
                handler(msg)
                return True
        else:
            return False
    
    def execute_page_callback(self, msg: PageCallbackEvent) -> None:
        """
        Executes the callback associated with the given PageQueryResponseEvent.
        """
        handler = self._page_bindings[msg.game_action]
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
            self.canvas.fill(self.base_color)  # Clear with transparent
            self._element_manager.render_all(self.canvas)
            self.gui_manager.draw_ui(self.canvas)
            return self.canvas
        else:
            return pygame.Surface((0, 0))  