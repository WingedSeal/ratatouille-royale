import pygame
import pygame_gui
from typing import Callable, Tuple

class WrappedWidget:
    """
    Base class for a wrapped UI element.
    Handles input detection, optional dragging, and custom rendering.
    """

    def __init__(
        self,
        manager: pygame_gui.UIManager,
        rect: pygame.Rect,
        render_callback: Callable[[pygame.Surface, Tuple[int, int]], None],
        draggable: bool = False,
        blocks_input: bool = True
    ):
        self.manager = manager
        self.render_callback = render_callback
        self.draggable = draggable
        self.blocks_input = blocks_input

        # Loads styling guide
        manager = pygame_gui.UIManager((800, 600), theme_path="theme.json")

        # Transparent panel to hold the internal UI element
        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=rect,
            manager=manager,
            object_id="#transparent_panel"
        )

        # Dragging state
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0

    def handle_event(self, event: pygame.event.Event):
        # Forward event to UIManager
        self.manager.process_events(event)

        # Handle dragging
        if self.draggable:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.panel.get_relative_rect().collidepoint(event.pos):
                    self.dragging = True
                    mouse_x, mouse_y = event.pos
                    self.offset_x = self.panel.get_relative_rect().x - mouse_x
                    self.offset_y = self.panel.get_relative_rect().y - mouse_y
            elif event.type == pygame.MOUSEBUTTONUP:
                self.dragging = False
            elif event.type == pygame.MOUSEMOTION and self.dragging:
                mouse_x, mouse_y = event.pos
                self.panel.set_relative_position((mouse_x + self.offset_x, mouse_y + self.offset_y))
                
    def draw(self, surface: pygame.Surface):
        # Draw the custom visual at the panel's current position
        pos = self.panel.get_relative_rect().topleft
        int_pos = (int(pos[0]), int(pos[1]))
        self.render_callback(surface, int_pos)

    def get_ui_element(self):
        """
        Returns the internal UI element that can be used for callback registration.
        For base widget, this might return the panel itself.
        """
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
        render_callback: Callable[[pygame.Surface, Tuple[int, int]], None],
        button_text: str = "",
        draggable: bool = True,
        blocks_input: bool = False,
        callback: Callable | None = None,
    ):
        super().__init__(manager, rect, render_callback, draggable, blocks_input)
        self.callback = callback

        # Internal UIButton for input detection
        self.button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, rect.width, rect.height),
            text=button_text,
            manager=manager,
            container=self.panel,
        )

    def handle_event(self, event: pygame.event.Event):
        # Handle button presses
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.button:
            if self.callback:
                self.callback()

        # Let base class handle dragging & UIManager processing
        super().handle_event(event)

    def get_ui_element(self):
        # Return the internal button for callback registration
        return self.button
    
    def show(self):
        super().show()
        self.button.show()

    def hide(self):
        super().hide()
        self.button.hide()