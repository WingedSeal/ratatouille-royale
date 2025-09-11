import pygame
from typing import Dict, List, Tuple
from ratroyale.input.constants import GestureKey, ActionKey
from ratroyale.event_tokens.input_token import GestureData
from ratroyale.visual.visual_component import VisualComponent, TileVisual, EntityVisual, REGULAR_TILE_SIZE
from ratroyale.backend.tile import Tile
from ratroyale.backend.entity import Entity
from abc import ABC, abstractmethod

class Hitbox(ABC):
    @abstractmethod
    def contains_point(self, point: Tuple[int, int]) -> bool:
        """Return True if the point is inside the hitbox."""
        pass
    @abstractmethod
    def draw(self, surface: pygame.Surface, color: Tuple[int, int, int] = (255, 0, 0)) -> None:
        """Draw the hitbox for debugging purposes."""
        pass

class RectangleHitbox(Hitbox):
    def __init__(self, rect: pygame.Rect):
        self.rect = rect

    def contains_point(self, point):
        return self.rect.collidepoint(point)

    def draw(self, surface, color=(0, 0, 255)):
        pygame.draw.rect(surface, color, self.rect, 1)


class CircleHitbox(Hitbox):
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    def contains_point(self, point):
        x, y = point
        cx, cy = self.center
        return (x - cx) ** 2 + (y - cy) ** 2 <= self.radius ** 2

    def draw(self, surface, color=(0, 255, 0)):
        pygame.draw.circle(surface, color, self.center, self.radius, 1)


# Hex hitbox
class HexHitbox(Hitbox):
    def __init__(self, center, width, height):
        """
        center: (x, y) of hex center
        width: distance from flat side to flat side (corner-to-corner horizontally)
        height: distance from point to opposite point vertically
        """
        self.cx, self.cy = center
        w, h = width / 2, height / 2

        # Precompute vertices (pointy-top, clockwise)
        self.points = [
            (self.cx,       self.cy - h),   # top
            (self.cx + w,   self.cy - h/2), # top-right
            (self.cx + w,   self.cy + h/2), # bottom-right
            (self.cx,       self.cy + h),   # bottom
            (self.cx - w,   self.cy + h/2), # bottom-left
            (self.cx - w,   self.cy - h/2)  # top-left
        ]

    def contains_point(self, point):
        # Simple ray-casting algorithm for polygons
        x, y = point
        inside = False
        n = len(self.points)
        for i in range(n):
            x1, y1 = self.points[i]
            x2, y2 = self.points[(i + 1) % n]
            if ((y1 > y) != (y2 > y)):
                slope = (x2 - x1) * (y - y1) / (y2 - y1) + x1
                if x < slope:
                    inside = not inside
        return inside

    def draw(self, surface, color=(0, 0, 255)):
        pygame.draw.polygon(surface, color, self.points, 1)


class Interactable:
    """
    Base class for a logical UI element.
    Handles hitbox-based input detection and optional visual component.
    """

    def __init__(
        self,
        hitbox: Hitbox,
        gesture_action_mapping: dict[GestureKey, ActionKey],
        visuals: list[VisualComponent] | None = None,
        blocks_input: bool = True,
        z_order: int = 0
    ):
        self.hitbox: Hitbox = hitbox
        self.gesture_action_mapping: dict[GestureKey, ActionKey] = gesture_action_mapping
        self.blocks_input: bool = blocks_input
        self.visuals: list[VisualComponent] = visuals or [] 
        self.z_order: int = z_order

    def process_gesture(self, gesture: GestureData) -> ActionKey | None:
        gesture_pos = gesture.start_pos
        if gesture_pos is None:
            return None
        if not self.hitbox.contains_point(gesture_pos):
            return None
        return self.gesture_action_mapping.get(gesture.gesture_key)

    def get_ui_element(self):
        """Return the visual element if any."""
        return self.visuals

    # def show(self):
    #     if self.visuals:
    #         self.visuals.show()

    # def hide(self):
    #     if self.visuals:
    #         self.visuals.hide()

class TileInteractable(Interactable):
    """
    Interactable specialized for tiles.
    Handles hitbox, tile-specific visuals, and any tile-specific input logic.
    """
    def __init__(self, tile: Tile, blocks_input: bool = True, z_order: int = 0):
        # Compute top-left for sprite placement
        tile_x, tile_y = TileVisual(tile)._hex_to_world(tile.coord, REGULAR_TILE_SIZE)

        # Correct hitbox center: shift by half width/height
        width, height = REGULAR_TILE_SIZE
        center_x, center_y = tile_x + width // 2, tile_y + height // 2
        hitbox = HexHitbox(center=(center_x, center_y), width=width, height=height)

        gesture_action_mapping = {
            GestureKey.CLICK: ActionKey.SELECT_TILE
        }

        visuals: List[VisualComponent] = [TileVisual(tile)]

        super().__init__(
            hitbox=hitbox,
            gesture_action_mapping=gesture_action_mapping,
            visuals=visuals,
            blocks_input=blocks_input,
            z_order=z_order
        )

class EntityInteractable(Interactable):
    """
    Interactable specialized for entities.
    Handles hitbox, entity-specific visuals, and any entity-specific input logic.
    """
    def __init__(self, entity: Entity, blocks_input: bool = True, z_order: int = 1):
        entity_visual = EntityVisual(entity)
        hitbox = RectangleHitbox(pygame.Rect(
            *entity_visual.position,
            entity_visual.image.get_width(),
            entity_visual.image.get_height()
        ))

        self.gesture_action_mapping = {
            GestureKey.CLICK: ActionKey.SELECT_UNIT
        }

        super().__init__(
            hitbox=hitbox,
            gesture_action_mapping=self.gesture_action_mapping,
            visuals=[entity_visual],
            blocks_input=blocks_input,
            z_order=z_order
        )


