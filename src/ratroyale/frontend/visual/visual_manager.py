import pygame
from ratroyale.visual.renderer import PageRenderer, GameBoardPageRenderer
from ratroyale.frontend.pages.page_definitions.page_creator import Page, GameBoardPage
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.visual_token import *
from typing import Callable
from ratroyale.frontend.page_management.page_name import PageName
from ratroyale.visual.screen_constants import SCREEN_SIZE

class VisualManager:
    def __init__(self, screen: pygame.Surface, coordination_manager: CoordinationManager) -> None:
        self.screen = screen
        self.coordination_manager = coordination_manager

        self.page_to_renderer_registry: dict[PageName, PageRenderer] = {}

        self.page_type_to_renderer: dict[PageName, type[PageRenderer]] = {
            PageName.GAME_BOARD: GameBoardPageRenderer
        }
        """Tells the renderer creator which method to use for this page name"""

        self.event_handlers: dict[type[VisualManagerEvent], Callable] = {
            RegisterPage_VisualManagerEvent: lambda tkn: self._register_renderer(tkn),
            UnregisterPage_VisualManagerEvent: lambda tkn: self._unregister_renderer(tkn)
        }

    # region Registration Methods

    def _register_renderer(self, tkn: VisualManagerEvent) -> None:
      """Associate a page with its renderer."""
      assert isinstance(tkn, RegisterPage_VisualManagerEvent)

      page = tkn.page_name
      renderer_cls = self.page_type_to_renderer.get(page, PageRenderer)
      renderer = renderer_cls(screen_size=SCREEN_SIZE, ui_manager=tkn.ui_manager)
      self.page_to_renderer_registry[page] = renderer

    def _unregister_renderer(self, tkn: VisualManagerEvent) -> None:
      """Remove a renderer if a page is closed or destroyed."""
      assert isinstance(tkn, UnregisterPage_VisualManagerEvent)

      page = tkn.page_name
      self.page_to_renderer_registry.pop(page, None)

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
              self._delegate(token)

    def _delegate(self, tkn: VisualManagerEvent) -> None:
        renderer = self.page_to_renderer_registry.get(tkn.page_name)
        if renderer:
            renderer.execute_callback(tkn)

    # endregion