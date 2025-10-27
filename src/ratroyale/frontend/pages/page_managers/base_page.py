from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol, cast

import pygame
import pygame_gui

from ratroyale.coordination_manager import CoordinationManager
from ratroyale.frontend.pages.page_elements.element import ElementWrapper
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.base import EventToken
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.input_token import get_id
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.visual_token import *
from ratroyale.frontend.gesture.gesture_data import GestureData
from ratroyale.frontend.pages.page_elements.element_manager import ElementManager
from ratroyale.frontend.pages.page_managers.event_binder import (
    input_event_bind,
    SpecialInputScope,
)
from ratroyale.frontend.pages.page_managers.theme_path_helper import resolve_theme_path
from ratroyale.frontend.pages.page_elements.spatial_component import Camera
from ...visual.anim.core.anim_structure import SequentialAnim

from ratroyale.frontend.visual.screen_constants import SCREEN_SIZE
from ratroyale.backend.game_event import GameEvent

from ratroyale.frontend.visual.anim.core.anim_coordinator import AnimationCoordinator

from typing import TypeVar

T = TypeVar("T", bound="ElementWrapper")


class InputHandler(Protocol):
    def __call__(self, event: pygame.event.Event) -> None: ...


class CallbackHandler(Protocol):
    def __call__(self, event: PageCallbackEvent) -> None: ...


class GameEventHandler(Protocol):
    def __call__(self, event: GameEvent) -> None: ...


class Page(ABC):
    """Base class for a page in the application."""

    def __init__(
        self,
        coordination_manager: CoordinationManager,
        camera: Camera,
        is_blocking: bool = True,
        theme_name: str = "default",
        base_color: tuple[int, int, int, int] | None = None,
    ) -> None:
        self.theme_path = str(resolve_theme_path(theme_name))
        self.gui_manager = pygame_gui.UIManager(SCREEN_SIZE, self.theme_path)
        """ Each page has its own UIManager """
        self.camera = camera
        self.coordination_manager = coordination_manager
        self.is_blocking: bool = is_blocking
        self._element_manager: ElementManager = ElementManager(
            self.gui_manager, self.coordination_manager, camera
        )
        self.canvas = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
        self.base_color: tuple[int, int, int, int] = (
            base_color if base_color else (0, 0, 0, 0)
        )
        self.is_visible: bool = True
        self.hovered: bool = False
        """ Pygame_gui elements will constantly fire hovered events instead of once during entry.
        Use this variable to keep track of scenarios where you want something to trigger only on beginning of hover. """

        self._input_bindings: dict[
            tuple[str | SpecialInputScope, int], InputHandler
        ] = {}
        """ Maps (element_id, gesture_type) to handler functions """
        self._callback_bindings: dict[str, CallbackHandler] = {}
        """ Maps (game_action) to handler functions """
        self._game_event_bindings: dict[type[GameEvent], GameEventHandler] = {}
        """ Maps (game_action) to handler functions """

        self._animation_coordinator: AnimationCoordinator = AnimationCoordinator()

        self.setup_event_bindings()

        gui_elements = self.define_initial_gui()
        self.setup_elements(gui_elements)

    @abstractmethod
    def define_initial_gui(self) -> list["ElementWrapper"]:
        """
        Return a list of UIRegisterForm (or other GUI element wrappers)
        that belong to this page. Even if the page has no elements,
        return an empty list.
        """
        ...

    @input_event_bind(SpecialInputScope.GLOBAL, pygame.QUIT)
    def quit_game(self, msg: pygame.event.Event) -> None:
        self.coordination_manager.stop_game()

    def queue_animation(
        self, anim_set: list[tuple[ElementWrapper, SequentialAnim]]
    ) -> None:
        self._animation_coordinator.queue_animation_set(anim_set)

    def setup_elements(self, configs: list[ElementWrapper]) -> None:
        for config in configs:
            self._element_manager.add_element(config)

    def get_element(
        self,
        element_id: str,
        element_group: str,
        cls: type[T] | None = None,
    ) -> T:
        element = self._element_manager.get_element(element_id, element_group)

        if cls is None:
            # type hint fallback
            return cast(T, element)

        if isinstance(element, cls):
            return element
        else:
            raise TypeError(
                f"Element is of type {type(element).__name__}, expected {cls.__name__}"
            )

    def close_self(self) -> None:
        self.post(
            PageNavigationEvent([(PageNavigation.CLOSE, f"{type(self).__name__}")])
        )

    def setup_event_bindings(self) -> None:
        """
        Scans all methods of the page instance for decorator metadata and
        populates the binding dictionaries.

        Supported decorators:
        - @input_event_bind -> stored in _input_bindings
            Binds element_id (a string name) and an event type (an integer) to a method.
        - @callback_event_bind  -> stored in _callback_bindings
            Binds an action name (a simple string) to a method.
        """
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if not callable(attr):
                continue

            # --- Input event bindings ---
            if hasattr(attr, "_input_bindings"):
                for element_id, event_type in getattr(attr, "_input_bindings"):
                    self._input_bindings[(element_id, event_type)] = cast(
                        InputHandler, attr
                    )

            # --- Callback event bindings ---
            if hasattr(attr, "_callback_bindings"):
                for page_event in getattr(attr, "_callback_bindings"):
                    self._callback_bindings[page_event] = cast(CallbackHandler, attr)

            # --- Game event bindings ---
            if hasattr(attr, "_game_event_bindings"):
                for game_event_type in getattr(attr, "_game_event_bindings"):
                    self._game_event_bindings[game_event_type] = cast(
                        GameEventHandler, attr
                    )

    def handle_gestures(self, gestures: list[GestureData]) -> list[GestureData]:
        """
        Dispatch a GestureData object to the appropriate Elements(s).

        - Elements always process gestures to update internal state.
        - If the page is hidden or not receiving input, no InputManagerEvent is produced.
        - Returns gestures that are unconsumed (for other pages).
        """
        if not self.is_visible:
            return gestures

        return self._element_manager.handle_gestures(gestures)

    def execute_input_callback(self, msg: pygame.event.Event) -> bool:
        """
        Executes all callbacks bound to the given InputManagerEvent.

        Supports:
        - Prefix matching for element IDs (e.g., 'inventory' matches 'inventory_slot_1')
        - Special input scope handlers for GLOBAL and UNCONSUMED events.

        Returns True if one or more handlers were executed.
        """
        element_id = self.get_leaf_object_id(get_id(msg))
        executed = False

        for (prefix, event_type), handler in self._input_bindings.items():
            if event_type != msg.type:
                continue

            if not isinstance(prefix, SpecialInputScope):
                if element_id and (
                    element_id == prefix or element_id.startswith(prefix)
                ):
                    handler(msg)
                    executed = True
            else:
                if prefix is SpecialInputScope.GLOBAL:
                    handler(msg)
                    executed = True
                elif prefix is SpecialInputScope.UNCONSUMED and not element_id:
                    handler(msg)
                    executed = True

        return executed

    def execute_page_callback(self, msg: PageCallbackEvent) -> bool:
        """
        Executes the callback associated with the given PageCallbackEvent.
        """
        executed = False
        for callback_action, handler in self._callback_bindings.items():
            if callback_action == msg.callback_action:
                handler(msg)
                executed = True
        return executed

    def execute_game_event_callback(self, msg: GameEvent) -> bool:
        """
        Executes the callback associated with the given PageCallbackEvent.
        """
        executed = False
        for callback_action, handler in self._game_event_bindings.items():
            if type(msg) is callback_action:
                handler(msg)
                executed = True
        return executed

    def get_leaf_object_id(self, object_id: str | None) -> str | None:
        """
        Given a fully-qualified pygame_gui object_id (with panel prefixes),
        returns only the last segment, which corresponds to the actual element.

        Example:
            'ability_panel_for_entity_TailBlazer_1_3.ability_0_from_entity_TailBlazer_1_3'
            -> 'ability_0_from_entity_TailBlazer_1_3'
        """
        return object_id.split(".")[-1] if object_id else None

    def execute_visual_callback(self, msg: VisualManagerEvent) -> None:
        pass

    def hide(self) -> None:
        self.is_visible = False

    def show(self) -> None:
        self.is_visible = True

    def on_open(self) -> None:
        """Called when the page is created. Override in subclasses if needed."""
        pass

    def on_close(self) -> None:
        """Called when the page is destroyed. Override in subclasses if needed."""
        self._element_manager.clear_all()

    def render(self, time_delta: float) -> pygame.Surface:
        if self.is_visible:
            self.gui_manager.update(time_delta)
            self._element_manager.update_all(time_delta)
            self._animation_coordinator.queue_to_elements()

            self.canvas.fill(self.base_color)  # Clear with transparent
            self._element_manager.render_all(self.canvas)
            self.gui_manager.draw_ui(self.canvas)
            return self.canvas
        else:
            return pygame.Surface((0, 0))

    def post(self, msg: EventToken) -> None:
        self.coordination_manager.put_message(msg)
