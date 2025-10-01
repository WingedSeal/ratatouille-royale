import pygame_gui

from .page_config import PageConfig
from ratroyale.event_tokens.input_token import InputManagerEvent
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.input.pages.interactables.interactable import InteractableMessage, Interactable
from ratroyale.visual.asset_management.visual_component import VisualComponent
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *
from ratroyale.visual.screen_constants import SCREEN_SIZE, THEME_PATH
from typing import cast, Callable
from ratroyale.input.pages.interactables.interactable import InteractableMessage
from typing import Generic, TypeVar
from ratroyale.input.gesture_management.gesture_data import GestureData, GestureType

T = TypeVar('T')

class Page(Generic[T]):
    """Base class for a page in the application."""
    def __init__(self, coordination_manager: CoordinationManager, is_blocking: bool = True) -> None:
        self.screen_size: tuple[int, int] = SCREEN_SIZE

        self.gui_manager = pygame_gui.UIManager(SCREEN_SIZE, THEME_PATH)
        """ Each page has its own UIManager """

        self.coordination_manager = coordination_manager

        self.is_blocking: bool = is_blocking

        self._interactables: list[Interactable] = []
        """ Registry for interactables (UI elements, tiles, cards, etc.) """

        self._interactable_bindings: dict[tuple[str, GestureType], Callable] = {}

        self._setup_bindings()

    def _setup_bindings(self):
        """
        Scan all methods of the page instance for `_bindings` metadata
        and populate _gesture_handlers.
        """
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, "_bindings"):
                for widget_id, gesture_type in attr._bindings:
                    self._interactable_bindings[(widget_id, gesture_type)] = attr

    def add_element(self, element: Interactable) -> None:
        self._interactables.append(element)

    def remove_element(self, element: Interactable) -> None:
        if element in self._interactables:
            self._interactables.remove(element)

    def handle_gestures(self, gestures: list[GestureData]) -> list[GestureData]:
        """
        Dispatch a GestureData object to the appropriate Interactable(s).
        Interactable then produces the corresponding InteractableMessage, which is
        handled by the page.
        """
        remaining_gestures: list[GestureData] = []

        for gesture in gestures:
            for interactable in self._interactables:
                interactable_message: InteractableMessage[T] | None = interactable.process_gesture(gesture)
                if interactable_message:
                    self.handle_interactable_message(interactable_message)

                    if interactable.blocks_input:
                        break
            else:
                remaining_gestures.append(gesture)

        return remaining_gestures
    
    def handle_interactable_message(self, msg: InteractableMessage) -> None:
        """
        Dispatch an InteractableMessage to the appropriate handler.
        """
        handler = self._interactable_bindings.get((msg.interactable_id, msg.gesture_data.gesture_type))
        if handler:
            handler(self, msg)
    
    def execute_callback(self, tkn: PageManagerEvent) -> None:
        pass