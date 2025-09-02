import pygame
import pygame_gui
from typing import Dict
from ratroyale.input.constants import GestureKey, ActionKey
from ratroyale.event_tokens import GestureData


class WrappedWidget:
    """
    Base class for a wrapped UI element.
    Handles input detection, hit-testing, and gesture → action mapping.
    """

    def __init__(
        self,
        manager: pygame_gui.UIManager,
        rect: pygame.Rect,
        gesture_action_mapping: Dict[GestureKey, ActionKey],
        blocks_input: bool = True
    ):
        self.manager = manager
        self.blocks_input = blocks_input
        self.gesture_action_mapping = gesture_action_mapping

        # Transparent panel serves as the widget's root container
        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=rect,
            manager=manager,
            object_id="#transparent_panel"
        )

    def process_gesture(self, gesture: GestureData) -> ActionKey | None:
        """
        Decide whether this widget cares about the gesture.
        Returns a simple ActionKey if it does, else None.
        """

        # 1. Find the gesture position
        gesture_pos = gesture.start_pos
        if gesture_pos is None:
            return None

        # 2. Check if it hits this widget's rect
        rect = self._get_absolute_rect()
        if rect is None:
            return None

        if not rect.collidepoint(gesture_pos):
            return None

        # 3. Map gesture to action
        return self.gesture_action_mapping.get(gesture.gesture_key)

    def _get_absolute_rect(self) -> pygame.Rect:
        rect = self.panel.get_relative_rect().copy()
        container = getattr(self.panel, "container", None)

        while container is not None:
            rect = rect.move(container.get_relative_rect().topleft)
            container = getattr(container, "container", None)

        return pygame.Rect(rect)  # cast to integer Rect

    def get_ui_element(self):
        """Return the internal UI element (panel)."""
        return self.panel

    def show(self):
        self.panel.show()

    def hide(self):
        self.panel.hide()

class WrappedButton(WrappedWidget):
    """
    A wrapped button: inherits dragging & custom rendering from WrappedWidget,
    but adds a UIButton for input detection and callback support.
    """

    def __init__(
        self,
        manager: pygame_gui.UIManager,
        rect: pygame.Rect,
        gesture_action_mapping: Dict[GestureKey, ActionKey],
        button_text: str = "",
        blocks_input: bool = False
    ):
        super().__init__(manager, rect, gesture_action_mapping, blocks_input)

        # Internal UIButton for input detection
        self.button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, rect.width, rect.height),
            text=button_text,
            manager=manager,
            container=self.panel,
        )

    def get_ui_element(self):
        # Return the internal button for callback registration
        return self.button
    
    def show(self):
        super().show()
        self.button.show()

    def hide(self):
        super().hide()
        self.button.hide()