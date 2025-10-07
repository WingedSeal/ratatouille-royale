from __future__ import annotations
import pygame_gui
import pygame

from ratroyale.event_tokens.input_token import get_id
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.frontend.pages.page_elements.element import Element
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *
from ratroyale.frontend.visual.screen_constants import SCREEN_SIZE
from typing import Callable
from ratroyale.frontend.gesture.gesture_data import GestureData, GestureType
from ratroyale.frontend.pages.page_elements.element_builder import ElementConfig, UIRegisterForm
from ratroyale.frontend.pages.page_elements.element_manager import ElementManager
from ratroyale.frontend.pages.page_managers.theme_path_helper import resolve_theme_path
from ratroyale.frontend.pages.page_managers.event_binder import input_event_bind


class Page():
    """Base class for a page in the application."""
    def __init__(
            self, 
            coordination_manager: CoordinationManager, 
            is_blocking: bool = True, 
            theme_name: str = "",
            base_color: tuple[int, int, int, int]  | None = None
            ) -> None:
        self.theme_path = str(resolve_theme_path(theme_name))
        self.gui_manager = pygame_gui.UIManager(SCREEN_SIZE, self.theme_path)
        """ Each page has its own UIManager """
        self.coordination_manager = coordination_manager
        self.is_blocking: bool = is_blocking
        self._element_manager: ElementManager = ElementManager(self.gui_manager, self.coordination_manager)
        self.canvas = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
        self.base_color: tuple[int, int, int, int] = base_color if base_color else (0, 0, 0, 0)
        self.is_visible: bool = True
        self.hovered: bool = False 
        """ Pygame_gui elements will constantly fire hovered events instead of once during entry.
        Use this variable to keep track of scenarios where you want something to trigger only on beginning of hover. """

        self._input_bindings: dict[tuple[str | None, GestureType], Callable] = {}
        """ Maps (element_id, gesture_type) to handler functions """
        self._callback_bindings: dict[str, Callable] = {}
        """ Maps (game_action) to handler functions """

        self.setup_input_bindings()

    @input_event_bind(None, pygame.QUIT)
    def quit_game(self, msg: pygame.event.Event):
        self.coordination_manager.stop_game()

    def setup_elements(self, configs: list[ElementConfig]) -> None:
        for config in configs:
            self._element_manager.create_element(config)

    def setup_gui_elements(self, ui_elements: list[UIRegisterForm]) -> None:
        for ui_element in ui_elements:
            self._element_manager.add_gui_element(ui_element.ui_element, ui_element.registered_name)

    def get_element(self, element_type: str, element_id: str) -> Element | None:
        return self._element_manager.get_element(element_type, element_id)

    def setup_input_bindings(self) -> None:
        """
        Scans all methods of the page instance for decorator metadata and
        populates the binding dictionaries.

        Supported decorators:
        - @input_event_bind -> stored in _input_bindings
        - @callback_event_bind  -> stored in _callback_bindings
        """
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if not callable(attr):
                continue

            # --- Input event bindings ---
            if hasattr(attr, "_input_bindings"):
                for element_id, event_type in getattr(attr, "_input_bindings"):
                    self._input_bindings[(element_id, event_type)] = attr

            # --- Page event bindings ---
            if hasattr(attr, "_callback_bindings"):
                for page_event in getattr(attr, "_callback_bindings"):
                    self._callback_bindings[page_event] = attr

    def handle_gestures(self, gestures: list[GestureData]) -> list[GestureData]:
        """
        Dispatch a GestureData object to the appropriate Interactable(s).
        Interactable then produces the corresponding InputManagerEvent, which is
        handled by the page.
        If the page is hidden, it will not process any gestures.
        """
        if not self.is_visible:
            return gestures

        return self._element_manager.handle_gestures(gestures)

    def execute_input_callback(self, msg: pygame.event.Event) -> bool:
        """
        Executes all callbacks bound to the given InputManagerEvent.

        Supports:
        - Prefix matching for element IDs (e.g., 'inventory' matches 'inventory_slot_1')
        - Global handlers with prefix=None for non-targeted events

        Returns True if one or more handlers were executed.
        """
        element_id = self.get_leaf_object_id(get_id(msg))

        # Call handlers that match either the event type and prefix
        return any(
            handler(msg)
            for (prefix, event_type), handler in self._input_bindings.items()
            if event_type == msg.type and (
                prefix is None or (element_id is not None and (element_id == prefix or element_id.startswith(prefix)))
            )
        )
    
    def get_leaf_object_id(self, object_id: str | None) -> str | None:
        """
        Given a fully-qualified pygame_gui object_id (with panel prefixes),
        returns only the last segment, which corresponds to the actual element.
        
        Example:
            'ability_panel_for_entity_TailBlazer_1_3.ability_0_from_entity_TailBlazer_1_3'
            -> 'ability_0_from_entity_TailBlazer_1_3'
        """
        return object_id.split('.')[-1] if object_id else None

    def execute_page_callback(self, msg: PageCallbackEvent) -> None:
        """
        Executes the callback associated with the given PageQueryResponseEvent.
        """
        handler = self._callback_bindings[msg.callback_action]
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