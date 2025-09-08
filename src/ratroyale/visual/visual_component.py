from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pygame_gui.core.ui_element import UIElement
import pygame
from ratroyale.backend.tile import Tile
from ratroyale.backend.entity import Entity
from ratroyale.visual.sprite_registry import SPRITE_REGISTRY, SpriteRegistryKey, REGULAR_TILE_SIZE

class VisualComponent(ABC):
    """Base class for anything that can be rendered as part of an Interactable."""

    @abstractmethod
    def create(self, manager=None):
        """Optional: create/init the visual. 
        For UI, this might need the gui_manager; for sprites, maybe not."""
        pass

    @abstractmethod
    def render(self, surface: pygame.Surface):
        """Draw this visual onto the given surface."""
        pass
    
@dataclass
class UIVisual(VisualComponent):
    type: type[UIElement]
    relative_rect: pygame.Rect
    text: str = ""
    kwargs: dict = field(default_factory=dict)
    instance: UIElement | None = None

    def create(self, manager):
        self.instance = self.type(
            relative_rect=self.relative_rect,
            manager=manager,
            **(self.kwargs or {})
        )

    def render(self, surface: pygame.Surface):
        # pygame_gui handles its own rendering,
        # so this might just be a no-op
        pass
    
class SpriteVisual(VisualComponent):
    def __init__(self, sprite_enum: SpriteRegistryKey, position: tuple[int, int]):
        # Look up the surface from the registry; fallback to DEFAULT_ENTITY if missing
        self.image = SPRITE_REGISTRY.get(
            sprite_enum, 
            SPRITE_REGISTRY[SpriteRegistryKey.DEFAULT_ENTITY]
        )
        self.position = position

    def create(self, manager=None):
        pass

    def render(self, surface: pygame.Surface):
        surface.blit(self.image, self.position)

class TileVisual(SpriteVisual):
    def __init__(self, tile: Tile):
        self.tile = tile
        pos = self._hex_to_world(tile.coord.x, tile.coord.y, REGULAR_TILE_SIZE)
        super().__init__(
            sprite_enum=getattr(tile, "sprite_variant", SpriteRegistryKey.DEFAULT_TILE),
            position=pos
        )

    def _hex_to_world(self, q: int, r: int, tile_size: tuple[int,int]) -> tuple[int,int]:
        width, height = tile_size
        x = width * (q + 0.5 * (r % 2))
        y = height * 0.75 * r
        return (int(x), int(y))   # top-left of tile
        
class EntityVisual(SpriteVisual):
    def __init__(self, entity: Entity):
        self.entity = entity
        super().__init__(
            sprite_enum=getattr(entity, "sprite_variant", SpriteRegistryKey.DEFAULT_ENTITY),
            position=self._hex_to_world(entity.pos.x, entity.pos.y, REGULAR_TILE_SIZE)
        )

    def _hex_to_world(self, q: int, r: int, tile_size: tuple[int, int]) -> tuple[int, int]:
        width, height = tile_size
        # base tile position (top-left of bounding box for the hex)
        x = width * (q + 0.5 * (r % 2))  
        y = height * 0.75 * r            

        # Adjust entity so its bottom is near bottom of hex
        entity_surface = SPRITE_REGISTRY[SpriteRegistryKey.DEFAULT_ENTITY]
        entity_w, entity_h = entity_surface.get_size()

        offset_x = (width - entity_w) // 2       # center horizontally in the hex
        offset_y = height - entity_h - 10         # 4px above the hex’s bottom edge

        return int(x + offset_x), int(y + offset_y)