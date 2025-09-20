import pygame

class PageRenderer:
  def __init__(self, screen_size: tuple[int, int]) -> None:
    self.canvas = pygame.Surface(screen_size, pygame.SRCALPHA)
    self.visuals = []

  def draw(self):
        self.canvas.fill((0,0,0,0))
        # Loop over visuals and render
        for v in self.visuals:
            v.render(self.canvas)

  pass