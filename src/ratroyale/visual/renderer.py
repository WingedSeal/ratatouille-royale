import pygame
from ratroyale.visual.asset_management.visual_component import VisualComponent
from ratroyale.input.page_management.interactable import Interactable

class PageRenderer:
  def __init__(self, screen_size: tuple[int, int]) -> None:
    self.canvas: pygame.Surface = pygame.Surface(screen_size, pygame.SRCALPHA)
    self.interactable_visuals: dict[Interactable, list[VisualComponent]] = {}
    # TODO: non-interactable visuals (e.g. particles)

  # TODO: layer order-based drawing
  def draw(self) -> None:
    self.canvas.fill((0,0,0,0))

    for visual_list in self.interactable_visuals.values():
      for visuals in visual_list:
        visuals.render(self.canvas)

  def register_component(self, interactable: Interactable, visual: VisualComponent) -> None:
    self.interactable_visuals.setdefault(interactable, []).append(visual)

  def unregister_component(self, interactable: Interactable) -> None:
    self.interactable_visuals.pop(interactable, None)

class GameBoardPageRenderer(PageRenderer):
  def __init__(self, screen_size: tuple[int,int]):
      super().__init__(screen_size)

  def highlight(self):
    pass
