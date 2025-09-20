import pygame
from ratroyale.visual.asset_management.visual_component import VisualComponent

class PageRenderer:
  def __init__(self, screen_size: tuple[int, int]) -> None:
    self.canvas: pygame.Surface = pygame.Surface(screen_size, pygame.SRCALPHA)
    self.visuals: list[VisualComponent] = []

  def draw(self) -> None:
    self.canvas.fill((0,0,0,0))

    for v in self.visuals:
      v.render(self.canvas)

class GameBoardPageRenderer(PageRenderer):
  def __init__(self, screen_size: tuple[int,int]):
      super().__init__(screen_size)
      self.tile_visuals: list[VisualComponent] = []
      self.entity_visuals: list[VisualComponent] = []

  def highlight(self):
    pass
  