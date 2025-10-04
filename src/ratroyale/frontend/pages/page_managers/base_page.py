import pygame_gui
import pygame

from ratroyale.event_tokens.input_token import InputManagerEvent
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.frontend.pages.interactables.interactable import Interactable
from ratroyale.frontend.pages.interactables.interactable_builder import InteractableConfig
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *
from ratroyale.frontend.visual.screen_constants import SCREEN_SIZE, THEME_PATH
from typing import Callable
from ratroyale.frontend.gesture.gesture_data import GestureData, GestureType
from ratroyale.frontend.pages.interactables.interactable_builder import create_interactable, InteractableConfig


class Page():
    """Base class for a page in the application."""
    def __init__(self, coordination_manager: CoordinationManager, is_blocking: bool = True) -> None:
        self.gui_manager = pygame_gui.UIManager(SCREEN_SIZE, THEME_PATH)
        """ Each page has its own UIManager """
        self.coordination_manager = coordination_manager
        self.is_blocking: bool = is_blocking
        self._interactables: list[Interactable] = []
        self.canvas = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
        self.is_visible: bool = True

        self._input_bindings: dict[tuple[str, GestureType], Callable] = {}
        """ Maps (interactable_id, gesture_type) to handler functions """
        self._page_bindings: dict[str, Callable] = {}
        """ Maps (interactable_id, gesture_type) to handler functions """

        self.setup_input_bindings()

    def setup_interactables(self, configs: list[InteractableConfig]) -> None:
        interactables: dict[str, Interactable] = {}

        # Pass 1 — build all interactables
        for cfg in configs:
            interactable = create_interactable(cfg, self.gui_manager)
            interactables[cfg.id] = interactable

        # Pass 2 — attach children if needed
        for cfg in configs:
            if cfg.parent_id:
                parent = interactables.get(cfg.parent_id)
                child = interactables[cfg.id]
                if parent is None:
                    raise ValueError(f"Parent interactable '{cfg.parent_id}' not found for child '{cfg.id}'")

                parent.add_child(child, cfg.offset)

        self._interactables = list(interactables.values())

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
        handler = self._input_bindings.get((msg.interactable_id, msg.gesture_data.gesture_type))
        if handler:
            handler(msg)
    
    def execute_page_callback(self, msg: PageQueryResponseEvent) -> None:
        """
        Executes the callback associated with the given PageQueryResponseEvent.
        """
        handler = self._page_bindings.get(msg.action_name)
        if handler:
            handler(msg)
    
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