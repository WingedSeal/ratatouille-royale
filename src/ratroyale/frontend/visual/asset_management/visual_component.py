from abc import ABC, abstractmethod

from dataclasses import dataclass, field
from pygame_gui.core.ui_element import UIElement
from pygame_gui.core.object_id import ObjectID
from pygame_gui.ui_manager import UIManager
import pygame
from ratroyale.backend.tile import Tile
from ratroyale.backend.entity import Entity
from ratroyale.frontend.pages.page_elements.element import Element
from ratroyale.frontend.visual.asset_management.sprite_registry import (
    SPRITE_REGISTRY,
    TYPICAL_TILE_SIZE,
)
from ratroyale.frontend.visual.asset_management.game_obj_to_sprite_registry import (
    SpriteRegistryKey,
    ENTITY_TO_SPRITE_REGISTRY,
    TILE_TO_SPRITE_REGISTRY,
)


class VisualComponent(ABC):
    """Base class for anything that can be rendered as part of an Element."""

    def create(self) -> None:
        """Create/init the visual.
        For UI, this might need the gui_manager; for sprites, maybe not."""
        pass

    def destroy(self) -> None:
        """Optional. Used for triggering the .kill() on pygame_gui elements"""
        pass

    @abstractmethod
    def render(self, surface: pygame.Surface) -> None:
        """Draw this visual onto the given surface."""
        ...

    @abstractmethod
    def set_position(self, topleft_coord: tuple[float, float]) -> None:
        """Move this visual component to the specified topleft coord"""
        ...

    @abstractmethod
    def set_highlighted(self, highlighted: bool) -> None:
        """Set whether this visual is highlighted (e.g. selected)"""
        ...


class UIElementVisual(VisualComponent):
    def __init__(self, ui_element: UIElement) -> None:
        self.ui_element: UIElement = ui_element

    def destroy(self) -> None:
        return self.ui_element.kill()  # type: ignore

    def render(self, surface: pygame.Surface) -> None:
        # pygame_gui handles rendering its own elements
        pass

    def set_position(self, topleft_coord: tuple[float, float]) -> None:
        self.ui_element.set_position(topleft_coord)

    def set_highlighted(self, highlighted: bool) -> None:
        # pygame_gui handles rendering its own elements, including highlighting.
        pass


class ElementVisual(VisualComponent):
    def __init__(self, element: Element) -> None:
        self.sprite: pygame.Surface = pygame.Surface(
            (200, 100)
        )  # placeholder. revise element to hold a sprite key that can be retrieved here later
        self.element: Element | None = element
        self.position: tuple[float, float] = element.get_topleft()
        self.highlighted: bool = False

    def destroy(self) -> None:
        self.element = None

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(self.sprite, self.position)

    def set_position(self, topleft_coord: tuple[float, float]) -> None:
        self.position = topleft_coord

    def set_highlighted(self, highlighted: bool) -> None:
        self.highlighted = highlighted


# class TileVisual(ElementVisual):
#     def __init__(self, tile: Tile) -> None:
#         super().__init__(
#             sprite_enum=TILE_TO_SPRITE_REGISTRY.get(
#                 type(tile), SpriteRegistryKey.DEFAULT_TILE
#             ),
#             position=tile.coord.to_pixel(*TYPICAL_TILE_SIZE, is_bounding_box=True),
#         )

#     def render(self, surface: pygame.Surface) -> None:
#         surface.blit(self.sprite, self.position)

#         if self.highlighted:
#             overlay = pygame.Surface(self.sprite.get_size(), pygame.SRCALPHA)
#             overlay.fill((255, 255, 0, 100))  # yellow with alpha
#             surface.blit(overlay, self.position)


# # TODO: re-implement entity visual offsets
# class EntityVisual(ElementVisual):
#     def __init__(self, entity: Entity) -> None:
#         sprite_key = ENTITY_TO_SPRITE_REGISTRY.get(
#             type(entity), SpriteRegistryKey.DEFAULT_ENTITY
#         )

#         pos = entity.pos.to_pixel(*TYPICAL_TILE_SIZE, is_bounding_box=True)

#         super().__init__(sprite_enum=sprite_key, position=pos)

#     def render(self, surface: pygame.Surface) -> None:
#         surface.blit(self.sprite, self.position)

#         if self.highlighted:
#             overlay = pygame.Surface(self.sprite.get_size(), pygame.SRCALPHA)
#             overlay.fill((255, 255, 0, 100))  # yellow with alpha
#             surface.blit(overlay, self.position)


# class AbilityMenuVisual(ElementVisual):
#     def __init__(
#         self,
#         skill_name: str,
#         topleft_pos: tuple[float, float],
#         font: pygame.font.Font | None = None,
#     ) -> None:
#         self.skill_name = skill_name
#         self.topleft_pos = topleft_pos

#         self.width = 100
#         self.height = 40

#         self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
#         self.rect = self.surface.get_rect(topleft=topleft_pos)

#         self.font = font or pygame.font.SysFont("Arial", 16)

#         self.highlighted = False

#         self._render_surface()

#     def _render_surface(self) -> None:
#         # Clear the surface
#         self.surface.fill((0, 0, 0, 0))  # transparent background

#         # Draw button background
#         bg_color = (200, 200, 200) if not self.highlighted else (255, 255, 100)
#         pygame.draw.rect(
#             self.surface, bg_color, (0, 0, self.width, self.height), border_radius=5
#         )

#         # Draw text
#         text_surf = self.font.render(self.skill_name, True, (0, 0, 0))
#         text_rect = text_surf.get_rect(center=(self.width // 2, self.height // 2))
#         self.surface.blit(text_surf, text_rect)

#     def set_highlight(self, highlighted: bool) -> None:
#         self.highlighted = highlighted
#         self._render_surface()

#     def render(self, target_surface: pygame.Surface) -> None:
#         target_surface.blit(self.surface, self.rect)
