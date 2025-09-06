from enum import Enum, auto
import pygame

def make_surface(size: tuple[int, int], color: tuple[int, int, int] | tuple[int, int, int, int], border_thickness: int = 3) -> pygame.Surface:
    surf = pygame.Surface(size, pygame.SRCALPHA)
    
    # Fill the main rectangle
    surf.fill(color)
    
    # Compute a darker version of the color for the border
    def darker(c):
        r, g, b, *rest = (*c, 255)  # ensure alpha present
        factor = 0.6  # darken by 40%
        return (int(r * factor), int(g * factor), int(b * factor), rest[0] if rest else 255)
    
    border_color = darker(color)
    
    # Draw the border rectangle
    pygame.draw.rect(surf, border_color, surf.get_rect(), border_thickness)
    
    return surf

class SpriteRegistryKey(Enum):
  DEFAULT_TILE = auto()
  DEFAULT_ENTITY = auto()

SPRITE_REGISTRY = {
    SpriteRegistryKey.DEFAULT_TILE: make_surface((64, 64), (0, 255, 0, 128)),
    SpriteRegistryKey.DEFAULT_ENTITY: make_surface((32, 32), (255, 0, 0, 255))
}

REGULAR_TILE_SIZE = (64, 64)