import pygame
from ratroyale.visual.renderer import PageRenderer
from ratroyale.input.page_management.page_creator import Page
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.visual_token import *
from typing import Callable

class VisualManager:
    def __init__(self, screen: pygame.Surface, coordination_manager: CoordinationManager) -> None:
        self.screen = screen
        self.page_to_renderer: dict[Page, PageRenderer] = {}
        self.coordination_manager = coordination_manager

        self.event_handlers: dict[type[VisualManagerEvent], Callable] = {
        }

    def register_renderer(self, page: Page, renderer: PageRenderer) -> None:
        """Associate a page with its renderer."""
        self.page_to_renderer[page] = renderer

    def unregister_renderer(self, page: Page) -> None:
        """Remove a renderer if a page is closed or destroyed."""
        if page in self.page_to_renderer:
            del self.page_to_renderer[page]

    def draw_all(self) -> None:
        """Delegate draw calls to all registered renderers and blit to screen."""
        for renderer in self.page_to_renderer.values():
            renderer.draw()  
            self.screen.blit(renderer.canvas, (0, 0))  

    def execute_callbacks(self) -> None:
      visual_event_queue = self.coordination_manager.mailboxes[VisualManagerEvent]

      while not visual_event_queue.empty():
          token = visual_event_queue.get()
          handler = self.event_handlers.get(type(token))
          if handler:
              handler(token)
          else:
              print(f"Unhandled page manager event: {token}")