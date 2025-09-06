import pygame
import pygame_gui
from typing import Dict, List
from ratroyale.input.constants import GestureKey, ActionKey
from ratroyale.event_tokens import GestureData
from ratroyale.visual.visual_component import VisualComponent, TileVisual, EntityVisual, REGULAR_TILE_SIZE
#from ratroyale.backend.tile import Tile    # Wait until the game logic guy fixes this.
from ratroyale.visual.dummy_game_objects import DummyTile, DummyEntity

# Base interface
class Hitbox:
    def contains_point(self, point):
        raise NotImplementedError

    def draw(self, surface, color=(255, 0, 0)):
        raise NotImplementedError


# Rectangle hitbox
class RectHitbox(Hitbox):
    def __init__(self, rect: pygame.Rect):
        self.rect = rect

    def contains_point(self, point):
        return self.rect.collidepoint(point)

    def draw(self, surface, color=(0, 0, 255)):
        pygame.draw.rect(surface, color, self.rect, 1)


# Circle hitbox
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
        gesture_action_mapping: Dict[GestureKey, ActionKey],
        visuals: list[VisualComponent] | None = None,
        blocks_input: bool = True,
        z_order: int = 0
    ):
        self.hitbox = hitbox
        self.gesture_action_mapping = gesture_action_mapping
        self.blocks_input = blocks_input
        self.visuals = visuals or [] # external UI element, optional
        self.z_order = z_order

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

"""
    Interactable specialized for tiles.
    Handles hitbox, tile-specific visuals, and any tile-specific input logic.
    """
class TileInteractable(Interactable):
    def __init__(self, tile: DummyTile, blocks_input: bool = True, z_order: int = 0):
        # Compute top-left for sprite placement
        tx, ty = TileVisual(tile)._hex_to_world(tile.coord.q, tile.coord.r, REGULAR_TILE_SIZE)

        # Correct hitbox center: shift by half width/height
        w, h = REGULAR_TILE_SIZE
        cx, cy = tx + w // 2, ty + h // 2
        hitbox = HexHitbox(center=(cx, cy), width=w, height=h)

        # Gesture mapping
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
    def __init__(self, entity: DummyEntity, blocks_input: bool = True, z_order: int = 1):
        entity_visual = EntityVisual(entity)
        hitbox = RectHitbox(pygame.Rect(
            *entity_visual.position,
            entity_visual.image.get_width(),
            entity_visual.image.get_height()
        ))

        # Gesture mapping
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


