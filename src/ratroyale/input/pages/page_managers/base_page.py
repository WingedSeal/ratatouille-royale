import pygame_gui
import pygame

from ratroyale.event_tokens.input_token import InputManagerEvent
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.input.pages.interactables.interactable import Interactable
from ratroyale.input.pages.interactables.interactable_builder import InteractableConfig
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *
from ratroyale.visual.screen_constants import SCREEN_SIZE, THEME_PATH
from typing import Callable
from ratroyale.input.gesture_management.gesture_data import GestureData, GestureType
from ratroyale.input.pages.interactables.interactable_builder import create_interactable, InteractableConfig


class Page():
    """Base class for a page in the application."""
    def __init__(self, coordination_manager: CoordinationManager, is_blocking: bool = True) -> None:
        self.gui_manager = pygame_gui.UIManager(SCREEN_SIZE, THEME_PATH)
        """ Each page has its own UIManager """
        self.coordination_manager = coordination_manager
        self.is_blocking: bool = is_blocking
        self._interactables: list[Interactable] = []
        self._interactable_bindings: dict[tuple[str, GestureType], Callable] = {}
        """ Maps (interactable_id, gesture_type) to handler functions """
        self.canvas = pygame.Surface(SCREEN_SIZE)
        self.is_visible: bool = True

    def setup_interactables(self, configs: list[InteractableConfig]) -> None:
        self._interactables = [create_interactable(cfg, self.gui_manager) for cfg in configs]
        self._sort_interactables_by_z_order()

    def setup_bindings(self) -> None:
        """
        Scan all methods of the page instance for `_bindings` metadata
        and populate _gesture_handlers.
        """
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, "_bindings"):
                for widget_id, gesture_type in attr._bindings:
                    self._interactable_bindings[(widget_id, gesture_type)] = attr

    def _sort_interactables_by_z_order(self) -> None:
        self._interactables.sort(key=lambda x: x.z_order, reverse=True)

    def add_element(self, element: Interactable) -> None:
        self._interactables.append(element)

    def remove_element(self, element: Interactable) -> None:
        if element in self._interactables:
            self._interactables.remove(element)

    def handle_gestures(self, gestures: list[GestureData]) -> list[GestureData]:
        """
        Dispatch a GestureData object to the appropriate Interactable(s).
        Interactable then produces the corresponding InputManagerEvent, which is
        handled by the page.
        Additionally, if the page is hidden, it will not process any gestures.
        """
        if not self.is_visible:
            return gestures

        remaining_gestures: list[GestureData] = []
        
        for gesture in gestures:
            for interactable in self._interactables:
                input_message: InputManagerEvent | None = interactable.process_gesture(gesture)
                if input_message:
                    self.coordination_manager.put_message(input_message)

                    if interactable.blocks_input:
                        break
            else:
                remaining_gestures.append(gesture)

        return remaining_gestures

    def execute_input_callback(self, msg: InputManagerEvent) -> None:
        """
        Executes the callback associated with the given InputManagerEvent.
        """
        handler = self._interactable_bindings.get((msg.interactable_id, msg.gesture_data.gesture_type))
        if handler:
            handler(msg)
    
    def execute_page_callback(self, msg: PageManagerEvent) -> None:
        pass
    
    def execute_visual_callback(self, msg: VisualManagerEvent) -> None:
        pass
    
    def hide(self) -> None:
      pass

    def show(self) -> None:
      pass

    def on_create(self) -> None:
      pass

    def on_destroy(self) -> None:
      pass

    def render(self, time_delta: float) -> pygame.Surface:
      self.gui_manager.update(time_delta)
      self.canvas.fill((0, 0, 0, 0))  # Clear with transparent

      # Draw UI components
      self.gui_manager.draw_ui(self.canvas)

      # Draw interactables
      for interactable in self._interactables:
          if interactable.visuals:
              for visual in interactable.visuals:
                visual.render(self.canvas)

      return self.canvas