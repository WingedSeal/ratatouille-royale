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
            RegisterPage_VisualManagerEvent: lambda tkn: self._register_renderer(tkn),
            UnregisterPage_VisualManagerEvent: lambda tkn: self._unregister_renderer(tkn),
            RegisterVisualComponent_VisualManagerEvent: lambda tkn: self._register_component(tkn),
            UnregisterVisualComponent_VisualManagerEvent: lambda tkn: print("Placeholder"),
            TileInteraction_VisualManagerEvent: lambda tkn: self._tile_interaction(tkn)
        }

    # region Registration Methods

    def _register_renderer(self, tkn: VisualManagerEvent) -> None:
      """Associate a page with its renderer."""
      assert isinstance(tkn, RegisterPage_VisualManagerEvent)

      print("Received message: Create", type(tkn.page))

      page = tkn.page  
      page_type = type(page)
      renderer_cls = self.page_type_to_renderer.get(page_type, PageRenderer)
      renderer = renderer_cls(screen_size=tkn.page.screen_size, ui_manager=tkn.ui_manager)
      self.page_to_renderer_registry[page] = renderer

    def _unregister_renderer(self, tkn: VisualManagerEvent) -> None:
      """Remove a renderer if a page is closed or destroyed."""
      assert isinstance(tkn, UnregisterPage_VisualManagerEvent)

      print("Received message: Destroy", type(tkn.page))

      page = tkn.page
      self.page_to_renderer_registry.pop(page, None)

    def _register_component(self, tkn: VisualManagerEvent) -> None:
        """Add visual component to the designated page"""
        assert isinstance(tkn, RegisterVisualComponent_VisualManagerEvent)

        print("Received message: Create", type(tkn.interactable))

        renderer = self.page_to_renderer_registry.get(tkn.page)
        
        if renderer:
          renderer.register_component(tkn.interactable, tkn.visual_component)
        else:
            print("No corresponding renderer found.")
    
    def _unregister_component(self, tkn: VisualManagerEvent) -> None:
        """Remove targeted visual component from the designated page"""
        assert isinstance(tkn, UnregisterVisualComponent_VisualManagerEvent)
        
        renderer = self.page_to_renderer_registry.get(tkn.page)

        if renderer:
           renderer.unregister_component(tkn.interactable)
    
    def _tile_interaction(self, tkn: VisualManagerEvent) -> None:
        """ Look for a renderer of type GameBoardPageRenderer among all registered pages,
          then forward the token to the page """
        for renderer in self.page_to_renderer_registry.items():
            if isinstance(renderer, GameBoardPageRenderer):
                renderer.execute_callback(tkn)
                break 

    # endregion

    def update(self, dt: float) -> None:
       """Update visual states based on delta time"""
       for renderer in reversed(self.page_to_renderer_registry.values()):
          renderer.update(dt)

    def draw(self) -> None:
        """Delegate draw calls to all registered renderers and blit to screen."""
        for renderer in self.page_to_renderer_registry.values():
            renderer.draw()  
            self.screen.blit(renderer.canvas, (0, 0))  

    # region Callback Execution

    def execute_callbacks(self) -> None:
      visual_event_queue = self.coordination_manager.mailboxes[VisualManagerEvent]

      while not visual_event_queue.empty():
          token = visual_event_queue.get()
          handler = self.event_handlers.get(type(token))
          if handler:
              handler(token)
          else:
              print(f"Unhandled page manager event: {token}")

    # endregion