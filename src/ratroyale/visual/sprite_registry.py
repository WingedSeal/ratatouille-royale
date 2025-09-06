from enum import Enum, auto
import pygame

def make_surface(size: tuple[int, int], color: tuple[int, int, int] | tuple[int, int, int, int]) -> pygame.Surface:
  surf = pygame.Surface(size, pygame.SRCALPHA)
  surf.fill(color)
  return surf

class SpriteRegistryKey(Enum):
  DEFAULT_TILE = auto()
  DEFAULT_ENTITY = auto()

SPRITE_REGISTRY = {
    SpriteRegistryKey.DEFAULT_TILE: make_surface((64, 64), (0, 0, 0, 128)),
    SpriteRegistryKey.DEFAULT_ENTITY: make_surface((32, 32), (255, 0, 0, 255))
}

REGULAR_TILE_SIZE = (25, 25)