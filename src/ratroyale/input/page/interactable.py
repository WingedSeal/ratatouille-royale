import pygame
import pygame_gui
from typing import Dict
from ratroyale.input.constants import GestureKey, ActionKey
from ratroyale.event_tokens import GestureData
from pygame_gui.core.ui_element import UIElement
from ratroyale.visual.visual_component import VisualComponent

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

    def draw(self, surface, color=(255, 0, 0)):
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
        width: horizontal distance from left-most to right-most
        height: vertical distance from top-most to bottom-most
        """
        self.cx, self.cy = center
        w, h = width / 2, height / 2
        # Precompute points
        self.points = [
            (self.cx - w / 2, self.cy - h),     # top-left
            (self.cx + w / 2, self.cy - h),     # top-right
            (self.cx + w, self.cy),             # mid-right
            (self.cx + w / 2, self.cy + h),     # bottom-right
            (self.cx - w / 2, self.cy + h),     # bottom-left
            (self.cx - w, self.cy),             # mid-left
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
        self.visuals = visuals  # external UI element, optional
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



