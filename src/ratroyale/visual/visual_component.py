from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pygame_gui.core.ui_element import UIElement
from pygame_gui.ui_manager import UIManager
import pygame
from ratroyale.backend.tile import Tile
from ratroyale.backend.entity import Entity
from ratroyale.backend.hexagon import OddRCoord
from ratroyale.visual.sprite_registry import SPRITE_REGISTRY, REGULAR_TILE_SIZE
from ratroyale.visual.game_obj_to_sprite_registry import SpriteRegistryKey, ENTITY_TO_SPRITE_REGISTRY, TILE_TO_SPRITE_REGISTRY

class VisualComponent(ABC):
    """Base class for anything that can be rendered as part of an Interactable."""

    @abstractmethod
    def create(self, manager: UIManager) -> None:
        """Optional: create/init the visual. 
        For UI, this might need the gui_manager; for sprites, maybe not."""
        ...

    @abstractmethod
    def render(self, surface: pygame.Surface) -> None:
        """Draw this visual onto the given surface."""
        ...
    
@dataclass
class UIVisual(VisualComponent):
    type: type[UIElement]
    relative_rect: pygame.Rect
    text: str = ""
    kwargs: dict = field(default_factory=dict)
    instance: UIElement | None = None

    def create(self, manager: UIManager) -> None:
        self.instance = self.type(
            relative_rect=self.relative_rect,
            manager=manager,
            **(self.kwargs or {})
        )

    def render(self, surface: pygame.Surface) -> None:
        # No-op, since pygame_gui handles rendering the UI components under its care.
        pass
    
class SpriteVisual(VisualComponent):
    def __init__(self, sprite_enum: SpriteRegistryKey, position: tuple[int, int]):
        # Look up the surface from the registry; fallback to DEFAULT_ENTITY if missing
        self.image = SPRITE_REGISTRY.get(
            sprite_enum, 
            SPRITE_REGISTRY[SpriteRegistryKey.DEFAULT_ENTITY]
        )
        self.position = position

    def create(self, manager=None) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(self.image, self.position)

class TileVisual(SpriteVisual):
    def __init__(self, tile: Tile):
        self.tile = tile

        sprite_key = TILE_TO_SPRITE_REGISTRY.get(type(tile), SpriteRegistryKey.DEFAULT_TILE)

        pos = self._hex_to_world(tile.coord, REGULAR_TILE_SIZE)

        super().__init__(
            sprite_enum=sprite_key,
            position=pos
        )

    def _hex_to_world(self, tile_coord: OddRCoord, tile_size: tuple[int,int]) -> tuple[int,int]:
        width, height = tile_size
        hex_q = tile_coord.x
        hex_r = tile_coord.y

        world_x = width * (hex_q + 0.5 * (hex_r % 2))
        world_y = height * 0.75 * hex_r
        return (int(world_x), int(world_y))   
        
class EntityVisual(SpriteVisual):
    def __init__(self, entity: Entity):
        self.entity = entity

        sprite_key = ENTITY_TO_SPRITE_REGISTRY.get(type(entity), SpriteRegistryKey.DEFAULT_ENTITY)

        super().__init__(
            sprite_enum=sprite_key,
            position=self._hex_to_world(entity.pos, REGULAR_TILE_SIZE)
        )

    def _hex_to_world(self, entity_coord: OddRCoord, tile_size: tuple[int, int]) -> tuple[int, int]:
        width, height = tile_size
        hex_q = entity_coord.x
        hex_r = entity_coord.y
        # base tile position (top-left of bounding box for the hex)
        world_x = width * (hex_q + 0.5 * (hex_r % 2))  
        world_y = height * 0.75 * hex_r            

        # Adjust entity so its bottom is near bottom of hex
        entity_surface = SPRITE_REGISTRY[SpriteRegistryKey.DEFAULT_ENTITY]
        entity_w, entity_h = entity_surface.get_size()

        offset_x = (width - entity_w) // 2       # center horizontally in the hex
        offset_y = height - entity_h - 10         # 4px above the hex’s bottom edge

        return int(world_x + offset_x), int(world_y + offset_y)