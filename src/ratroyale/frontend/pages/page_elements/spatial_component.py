from dataclasses import dataclass
from typing import Literal

import pygame

from ratroyale.frontend.visual.screen_constants import SCREEN_SIZE_HALVED

SpaceMode = Literal["WORLD", "SCREEN"]


# TODO: Move camera class to element?
@dataclass
class Camera:
    world_x: float
    world_y: float
    screen_offset_x: float
    screen_offset_y: float
    scale: float = 1.0
    scale_constraints: tuple[float, float] = (1.5, 0.5)
    """Upper and lower bound for zooming scale"""

    _dirty: bool = True
    """Marks if the camera has moved or zoomed"""

    # Temporary drag state
    _prev_drag_mouse: tuple[float, float] | None = None

    def set_scale_constraints(self, constraint: tuple[float, float]) -> None:
        self.scale_constraints = constraint

    def world_to_screen(self, wx: float, wy: float) -> tuple[float, float]:
        """Convert a world coordinate to screen coordinate."""
        sx = (wx - self.world_x) * self.scale + self.screen_offset_x
        sy = (wy - self.world_y) * self.scale + self.screen_offset_y
        return sx, sy

    def screen_to_world(self, sx: float, sy: float) -> tuple[float, float]:
        """Convert a screen coordinate back to world coordinate."""
        wx = self.world_x + (sx - self.screen_offset_x) / self.scale
        wy = self.world_y + (sy - self.screen_offset_y) / self.scale
        return wx, wy

    def zoom_at(
        self, new_scale: float, screen_pos: tuple[float, float] | None = None
    ) -> None:
        """
        Zoom the camera while keeping the world point under (screen_px, screen_py)
        locked to the same screen position.
        """
        # Clamp new scale to constraints
        min_scale, max_scale = self.scale_constraints[1], self.scale_constraints[0]
        new_scale = max(min_scale, min(max_scale, new_scale))

        screen_px = SCREEN_SIZE_HALVED[0] if not screen_pos else screen_pos[0]
        screen_py = SCREEN_SIZE_HALVED[1] if not screen_pos else screen_pos[1]

        # World point under cursor before zoom
        wx, wy = self.screen_to_world(screen_px, screen_py)

        # Apply zoom
        self.scale = new_scale

        # Recalculate world origin so (wx, wy) stays under same screen pixel
        self.world_x = wx - (screen_px - self.screen_offset_x) / self.scale
        self.world_y = wy - (screen_py - self.screen_offset_y) / self.scale

        self._dirty = True

    def move_by(self, dx: float, dy: float) -> None:
        """Pan camera by screen-space delta."""
        self.world_x += dx / self.scale
        self.world_y += dy / self.scale

        self._dirty = True

    def move_to(self, x: float, y: float) -> None:
        self.world_x = x
        self.world_y = y

        self._dirty = True

    def start_drag(self, screen_pos: tuple[float, float]) -> None:
        """Call when drag starts with no entity."""
        self._prev_drag_mouse = screen_pos

    def drag_to(self, screen_pos: tuple[float, float]) -> None:
        """Call while dragging with no entity; moves camera opposite to mouse movement."""
        if self._prev_drag_mouse is None:
            self._prev_drag_mouse = screen_pos
            return

        dx = screen_pos[0] - self._prev_drag_mouse[0]
        dy = screen_pos[1] - self._prev_drag_mouse[1]

        # Move opposite to drag direction, scaled to world coordinates
        self.move_by(-dx, -dy)

        self._prev_drag_mouse = screen_pos

    def end_drag(self) -> None:
        """Call when drag ends."""
        self._prev_drag_mouse = None

    def clear_dirty(self) -> None:
        self._dirty = False


@dataclass
class SpatialComponent:
    """Authoritative object to dictate position and size of an element."""

    local_rect: pygame.Rect | pygame.FRect
    scale: float = 1.0
    z_order: int = 0
    space_mode: str = "SCREEN"
    _cached_screen_rect: pygame.Rect | pygame.FRect | None = None

    def get_screen_rect(self, camera: "Camera") -> pygame.Rect | pygame.FRect:
        if self._cached_screen_rect is not None and not camera._dirty:
            return self._cached_screen_rect

        # Recompute screen rect
        if self.space_mode == "WORLD":
            x, y = self.local_rect.center
            sx, sy = camera.world_to_screen(x, y)
            total_scale = camera.scale * self.scale
            w = self.local_rect.width * total_scale
            h = self.local_rect.height * total_scale
            rect: pygame.Rect | pygame.FRect = pygame.Rect(sx - w / 2, sy - h / 2, w, h)
        else:
            rect = self.local_rect.copy()

        self._cached_screen_rect = rect
        return rect

    def get_relative_rect(self, camera: "Camera") -> pygame.Rect | pygame.FRect:
        """
        Returns the rect scaled relative to its top-left corner.
        - For SCREEN space: applies only self.scale.
        - For WORLD space: applies both self.scale and camera.scale.
        Does not apply any positional transformation.
        """
        rect = self.local_rect.copy()

        # Determine total scale based on space mode
        total_scale = (
            self.scale * camera.scale if self.space_mode == "WORLD" else self.scale
        )

        if total_scale != 1.0:
            rect.width *= total_scale
            rect.height *= total_scale
            # Top-left remains the same; no need to adjust rect.topleft

        return rect

    def invalidate_cache(self) -> None:
        """Call if element moves or scale changes to force recalculation."""
        self._cached_screen_rect = None
        self._cached_camera_pos = None

    def get_rect(self) -> pygame.Rect | pygame.FRect:
        return self.local_rect

    def get_center_of_local_rect(self) -> tuple[float, float]:
        return (
            self.local_rect.x + self.local_rect.width / 2,
            self.local_rect.y + self.local_rect.height / 2,
        )

    def set_position(self, topleft: tuple[float, float]) -> None:
        self.local_rect.topleft = topleft

    def add_position(self, delta_topleft: tuple[float, float]) -> None:
        new_topleft_x = self.local_rect.x + delta_topleft[0]
        new_topleft_y = self.local_rect.y + delta_topleft[1]
        self.set_position((new_topleft_x, new_topleft_y))

    def set_size(self, size: tuple[float, float]) -> None:
        self.local_rect.size = size

    def center_to_screen_pos(
        self, screen_pos: tuple[float, float], camera: Camera
    ) -> None:
        """Move element so that its center aligns with a given screen position."""
        width, height = self.get_screen_rect(camera).size
        new_x = screen_pos[0] - width // 2
        new_y = screen_pos[1] - height // 2

        self.set_position(
            camera.screen_to_world(new_x, new_y)
            if self.space_mode == "WORLD"
            else (new_x, new_y)
        )
