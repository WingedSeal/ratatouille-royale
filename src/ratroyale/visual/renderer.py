import pygame
from ratroyale.visual.asset_management.visual_component import VisualComponent
from ratroyale.input.page_management.interactable import Interactable
from pygame_gui.ui_manager import UIManager
from ratroyale.visual.asset_management.visual_component import UIVisual, SpriteVisual

class PageRenderer:
  def __init__(self, screen_size: tuple[int, int], ui_manager: UIManager) -> None:
    self.canvas: pygame.Surface = pygame.Surface(screen_size, pygame.SRCALPHA)
    self.ui_manager: UIManager = ui_manager
    self.interactable_visuals: dict[Interactable, list[VisualComponent]] = {}
    # TODO: non-interactable visuals (e.g. particles)

  def update(self, dt: float) -> None:
    self.ui_manager.update(dt)

  # TODO: layer order-based drawing
  def draw(self) -> None:
    self.canvas.fill((0,0,0,0))

    for visual_list in self.interactable_visuals.values():
      for visuals in visual_list:
        visuals.render(self.canvas)

    self.ui_manager.draw_ui(self.canvas)

  def register_component(self, interactable: Interactable, visual: list[VisualComponent]) -> None:
    self.interactable_visuals.setdefault(interactable, []).extend(visual)

  def unregister_component(self, interactable: Interactable) -> None:
    self.interactable_visuals.pop(interactable, None)

class GameBoardPageRenderer(PageRenderer):
  def __init__(self, screen_size: tuple[int,int], ui_manager: UIManager) -> None:
      super().__init__(screen_size, ui_manager)

  def highlight(self) -> None:
    pass
