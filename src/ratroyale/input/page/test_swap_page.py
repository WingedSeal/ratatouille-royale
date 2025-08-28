from .page import Page
import pygame_gui
import pygame

class TestSwapPage(Page):
    def __init__(self, gui_manager, container_rect, return_callback=None):
        super().__init__("Swap Test Page", gui_manager, container_rect)

        # Add buttons and callbacks
        return_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((100, 100), (200, 50)),
            text="Return to Main Menu",
            manager=gui_manager
        )

        self.add_element(return_button, callback=return_callback)