from abc import ABC, abstractmethod

from dataclasses import dataclass, field
from pygame_gui.core.ui_element import UIElement
from pygame_gui.ui_manager import UIManager
import pygame
from ratroyale.backend.tile import Tile
from ratroyale.backend.entity import Entity
from ratroyale.visual.asset_management.sprite_registry import SPRITE_REGISTRY, TYPICAL_TILE_SIZE
from ratroyale.visual.asset_management.game_obj_to_sprite_registry import SpriteRegistryKey, ENTITY_TO_SPRITE_REGISTRY, TILE_TO_SPRITE_REGISTRY

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
    def __init__(self, sprite_enum: SpriteRegistryKey, position: tuple[float, float]) -> None:
        # Look up the surface from the registry; fallback to DEFAULT_ENTITY if missing
        self.image = SPRITE_REGISTRY.get(
            sprite_enum, 
            SPRITE_REGISTRY[SpriteRegistryKey.DEFAULT_ENTITY]
        )
        self.position = position

    def create(self, manager: UIManager) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(self.image, self.position)

class TileVisual(SpriteVisual):
    def __init__(self, tile: Tile) -> None:
        self.tile = tile

        super().__init__(
            sprite_enum=TILE_TO_SPRITE_REGISTRY.get(type(tile), SpriteRegistryKey.DEFAULT_TILE),
            position=tile.coord.to_pixel(*TYPICAL_TILE_SIZE, is_bounding_box=True)
        )


    def render(self, surface: pygame.Surface, highlighted: bool) -> None:
        surface.blit(self.image, self.position)

        if highlighted:
            overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            overlay.fill((255, 255, 0, 100))  # yellow with alpha
            surface.blit(overlay, self.position)


# TODO: re-implement entity visual offsets
class EntityVisual(SpriteVisual):
    def __init__(self, entity: Entity) -> None:
        self.entity = entity

        sprite_key = ENTITY_TO_SPRITE_REGISTRY.get(type(entity), SpriteRegistryKey.DEFAULT_ENTITY)

        pos = entity.pos.to_pixel(*TYPICAL_TILE_SIZE, is_bounding_box=True)

        super().__init__(
            sprite_enum=sprite_key,
            position=pos
        )

    def render(self, surface: pygame.Surface, highlighted: bool) -> None:
        surface.blit(self.image, self.position)

        if highlighted:
            overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            overlay.fill((255, 255, 0, 100))  # yellow with alpha
            surface.blit(overlay, self.position)