from .page import Page
import pygame_gui
import pygame

class MainMenuPage(Page):
    def __init__(self, gui_manager, start_callback=None, quit_callback=None):
        super().__init__("Main Menu")

        # Add buttons and callbacks
        start_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((100, 100), (200, 50)),
            text="Start Game",
            manager=gui_manager
        )
        quit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((100, 200), (200, 50)),
            text="Quit",
            manager=gui_manager
        )

        self.add_element(start_button, callback=start_callback)
        self.add_element(quit_button, callback=quit_callback)