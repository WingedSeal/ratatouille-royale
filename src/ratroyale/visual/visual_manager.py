import pygame
from ratroyale.visual.renderer import PageRenderer, GameBoardPageRenderer
from ratroyale.input.page_management.page_creator import Page, GameBoardPage
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.visual_token import *
from typing import Callable

class VisualManager:
    def __init__(self, screen: pygame.Surface, coordination_manager: CoordinationManager) -> None:
        self.screen = screen
        self.coordination_manager = coordination_manager

        self.page_to_renderer_registry: dict[Page, PageRenderer] = {}

        self.page_type_to_renderer: dict[type[Page], type[PageRenderer]] = {
            Page: PageRenderer,
            GameBoardPage: GameBoardPageRenderer
        }

        self.event_handlers: dict[type[VisualManagerEvent], Callable] = {
            RegisterPage_VisualManagerEvent: lambda tkn: self.register_renderer(tkn),
            UnregisterPage_VisualManagerEvent: lambda tkn: self.unregister_renderer(tkn),
            RegisterVisualComponent_VisualManagerEvent: lambda tkn: self.register_component(tkn),
        }

    def register_renderer(self, tkn: VisualManagerEvent) -> None:
      """Associate a page with its renderer."""
      assert isinstance(tkn, RegisterPage_VisualManagerEvent)

      page = tkn.page  
      page_type = type(page)
      renderer_cls = self.page_type_to_renderer.get(page_type, PageRenderer)
      renderer = renderer_cls(screen_size=tkn.page.screen_size)
      self.page_to_renderer_registry[page] = renderer

    def unregister_renderer(self, tkn: VisualManagerEvent) -> None:
      """Remove a renderer if a page is closed or destroyed."""
      assert isinstance(tkn, UnregisterPage_VisualManagerEvent)

      page = tkn.page
      self.page_to_renderer_registry.pop(page, None)

    def register_component(self, tkn: VisualManagerEvent) -> None:
        """Add visual component to the designated page"""
        assert isinstance(tkn, RegisterVisualComponent_VisualManagerEvent)

        renderer = self.page_to_renderer_registry.get(tkn.page)
        
        if renderer:
          renderer.register_component(tkn.interactable ,tkn.visual_component)
    
    def unregister_component(self, tkn: VisualManagerEvent) -> None:
        """Remove targeted visual component from the designated page"""
        assert isinstance(tkn, UnregisterVisualComponent_VisualManagerEvent)
        
        renderer = self.page_to_renderer_registry.get(tkn.page)

        if renderer:
           renderer.unregister_component(tkn.interactable)

    def draw_all(self) -> None:
        """Delegate draw calls to all registered renderers and blit to screen."""
        for renderer in self.page_to_renderer_registry.values():
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