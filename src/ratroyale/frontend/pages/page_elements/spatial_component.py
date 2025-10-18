from dataclasses import dataclass
import pygame
from typing import Literal
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

    def move_by(self, dx: float, dy: float) -> None:
        """Pan camera by screen-space delta."""
        self.world_x += dx / self.scale
        self.world_y += dy / self.scale

    def move_to(self, x: float, y: float) -> None:
        self.world_x = x
        self.world_y = y

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


@dataclass
class SpatialComponent:
    """Authoritative object to dictate position and size of an element."""

    local_rect: pygame.Rect | pygame.FRect
    scale: float = 1.0
    z_order: int = 0
    space_mode: SpaceMode = "SCREEN"

    def get_screen_rect(self, camera: "Camera") -> pygame.Rect | pygame.FRect:
        if self.space_mode == "WORLD":
            x, y = self.local_rect.topleft
            total_scale = camera.scale * self.scale
            sx, sy = camera.world_to_screen(x, y)
            w = self.local_rect.width * total_scale
            h = self.local_rect.height * total_scale
            rect: pygame.Rect | pygame.FRect = pygame.Rect(sx, sy, w, h)
        else:
            rect = self.local_rect.copy()
        return rect

    def get_rect(self) -> pygame.Rect | pygame.FRect:
        return self.local_rect

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
