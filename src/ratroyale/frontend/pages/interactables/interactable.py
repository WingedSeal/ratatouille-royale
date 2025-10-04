import pygame
import pygame_gui

from pygame_gui import UIManager
from ratroyale.frontend.gesture.gesture_data import GestureData
from ratroyale.frontend.visual.asset_management.visual_component import VisualComponent
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Callable
from ratroyale.event_tokens.input_token import InputManagerEvent
from enum import Enum, auto
from ratroyale.frontend.visual.asset_management.visual_component import UIVisual, TileVisual

# region Base Hitbox Classes

class Hitbox(ABC):
    @abstractmethod
    def contains_point(self, point: tuple[float, float]) -> bool:
        """Return True if the point is inside the hitbox."""
        ...
    @abstractmethod
    def draw(self, surface: pygame.Surface, color: tuple[int, int, int] = (255, 0, 0)) -> None:
        """Draw the hitbox for debugging purposes."""
        ...
    @abstractmethod
    def move_to(self, topleft_coord: tuple[float, float]) -> None:
        """Move the hitbox to a new topleft coordinate"""
        ...
    @abstractmethod
    def get_topleft(self) -> tuple[float, float]:
        ...

class RectangleHitbox(Hitbox):
    def __init__(self, rect: pygame.Rect) -> None:
        self.rect = rect

    def contains_point(self, point: tuple[float, float]) -> bool:
        return self.rect.collidepoint(point)

    def draw(self, surface: pygame.Surface, color: tuple[int, int, int]=(0, 0, 255)) -> None:
        pygame.draw.rect(surface, color, self.rect, 1)

    def move_to(self, topleft_coord: tuple[float, float]) -> None:
        self.rect.topleft = topleft_coord

    def get_topleft(self) -> tuple[float, float]:
        return self.rect.topleft

class CircleHitbox(Hitbox):
    def __init__(self, center: tuple[float, float], radius: int) -> None:
        self.center = center
        self.radius = radius

    def contains_point(self, point: tuple[float, float]) -> bool:
        x, y = point
        cx, cy = self.center
        return (x - cx) ** 2 + (y - cy) ** 2 <= self.radius ** 2

    def draw(self, surface: pygame.Surface, color: tuple[int, int, int]=(0, 255, 0)) -> None:
        pygame.draw.circle(surface, color, self.center, self.radius, 1)

    def move_to(self, topleft_coord: tuple[float, float]) -> None:
        ...

    def get_topleft(self) -> tuple[float, float]:
        return (self.center[0] - self.radius, self.center[1] + self.radius)

# TODO: could change this to polygonal hitbox and move all hex related functions to hexagon.py
class HexHitbox(Hitbox):
    def __init__(self, topleft: tuple[float, float], width: float, height: float) -> None:
        """
        topleft: (x, y) of the top-left bounding box of the hex
        width: corner-to-corner horizontally
        height: point-to-point vertically
        """
        self.topleft = topleft
        self.width = width
        self.height = height
        # Convert top-left to center
        cx = topleft[0] + width / 2
        cy = topleft[1] + height / 2
        self.move_to_center((cx, cy))

    def _compute_points(self, center: tuple[float, float]) -> list[tuple[float, float]]:
        cx, cy = center
        w, h = self.width / 2, self.height / 2
        return [
            (cx,     cy - h),    # top
            (cx + w, cy - h/2),  # top-right
            (cx + w, cy + h/2),  # bottom-right
            (cx,     cy + h),    # bottom
            (cx - w, cy + h/2),  # bottom-left
            (cx - w, cy - h/2)   # top-left
        ]
    
    def contains_point(self, point: tuple[float, float]) -> bool:
        # Ray-casting algorithm for convex polygon
        x, y = point
        inside = False
        n = len(self.points)
        for i in range(n):
            x1, y1 = self.points[i]
            x2, y2 = self.points[(i + 1) % n]
            if (y1 > y) != (y2 > y):
                slope = (x2 - x1) * (y - y1) / (y2 - y1) + x1
                if x < slope:
                    inside = not inside
        return inside

    def move_to(self, topleft_coord: tuple[float, float]) -> None:
        """Move the hitbox so that the top-left of its bounding box is at `topleft`."""
        cx = topleft_coord[0] + self.width / 2
        cy = topleft_coord[1] + self.height / 2
        self.move_to_center((cx, cy))

    def move_to_center(self, center: tuple[float, float]) -> None:
        """Move the hitbox so that its center is at `center`."""
        self.cx, self.cy = center
        self.points = self._compute_points(center)

    def draw(self, surface: pygame.Surface, color: tuple[int, int, int] = (0, 0, 255)) -> None:
        pygame.draw.polygon(surface, color, self.points, 1)

    def get_topleft(self) -> tuple[float, float]:
        return self.topleft

 # endregion

# region Base Interactable

T = TypeVar("T")

class Interactable(Generic[T]):
    """
    Base class for a logical UI element.
    Handles hitbox-based input detection and optional visual component.
    """
    def __init__(
        self,
        interactable_id: str,
        hitbox: Hitbox,
        payload: T | None = None,
        blocks_input: bool = True,
        z_order: int = 0,
        visuals: list[VisualComponent] | None = None
    ) -> None:
        self.interactable_id: str = interactable_id
        self.hitbox: Hitbox = hitbox
        self.payload: T | None = payload
        self.blocks_input: bool = blocks_input

        self.z_order: int = z_order
        self.visuals: list[VisualComponent] = visuals if visuals else []

    def process_gesture(self, gesture: GestureData) -> InputManagerEvent | None:
        gesture_pos = gesture.start_pos
        if gesture_pos is None:
            return None
        if not self.hitbox.contains_point(gesture_pos):
            return None
        return InputManagerEvent(
            interactable_id=self.interactable_id,
            gesture_data=gesture,
            payload=self.payload)
    
    def get_topleft(self) -> tuple[float, float]:
        return self.hitbox.get_topleft()

    def attach_visuals(self, visuals: VisualComponent) -> None:
        self.visuals.append(visuals)

# endregion


# class TileInteractable(Interactable):
#     """
#     Interactable specialized for tiles.
#     Handles hitbox, tile-specific visuals, and any tile-specific input logic.
#     """
#     def __init__(self, tile: Tile, blocks_input: bool = True, z_order: int = 0) -> None:
#         self.tile = tile

#         # Compute top-left for hitbox placement
#         tile_x, tile_y = tile.coord.to_pixel(*TYPICAL_TILE_SIZE, is_bounding_box=True)
#         width, height = TYPICAL_TILE_SIZE

#         # Create hitbox using top-left directly
#         hitbox = HexHitbox(topleft=(tile_x, tile_y), width=width, height=height)

#         gesture_action_mapping = {
#             GestureType.CLICK: ActionName.SELECT_TILE
#         }

#         super().__init__(
#             hitbox=hitbox,
#             gesture_action_mapping=gesture_action_mapping,
#             blocks_input=blocks_input,
#             z_order=z_order
#         )

#     def get_tile_coord(self) -> tuple[int, int]:
#         return (self.tile.coord.row, self.tile.coord.col)

# class EntityInteractable(Interactable):
#     """
#     Interactable specialized for entities.
#     Handles hitbox, entity-specific visuals, and any entity-specific input logic.
#     """
#     def __init__(self, entity: Entity, blocks_input: bool = True, z_order: int = 1) -> None:
#         self.entity = entity
#         entity_visual = EntityVisual(entity)
#         hitbox = RectangleHitbox(pygame.Rect(
#             *entity_visual.position,
#             entity_visual.image.get_width(),
#             entity_visual.image.get_height()
#         ))

#         gesture_action_mapping = {
#             GestureType.CLICK: ActionName.SELECT_UNIT,
#             GestureType.DOUBLE_CLICK: ActionName.DISPLAY_ABILITY_MENU
#         }

#         super().__init__(
#             hitbox=hitbox,
#             gesture_action_mapping=gesture_action_mapping,
#             blocks_input=blocks_input,
#             z_order=z_order
#         )

# class AbilityMenuInteractable(Interactable):
#     """
#     Interactable specialized for ability menu selections
#     """

#     def __init__(self, rect: pygame.Rect, blocks_input: bool = True, z_order: int = 1) -> None:
#         hitbox = RectangleHitbox(rect)

#         gesture_action_mapping = {
#             GestureType.CLICK: ActionName.SELECT_ABILITY
#         }

#         super().__init__(
#             hitbox=hitbox,
#             gesture_action_mapping=gesture_action_mapping,
#             blocks_input=blocks_input,
#             z_order=z_order
#         )


