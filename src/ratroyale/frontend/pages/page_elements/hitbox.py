import pygame

from abc import ABC, abstractmethod
from .spatial_component import SpatialComponent, Camera


class Hitbox(ABC):

    def _bind(self, spatial_component: SpatialComponent, camera: Camera) -> None:
        self._spatial_component = spatial_component
        self._camera = camera

    def _require_bind(self) -> None:
        if not hasattr(self, "_spatial_component") or not hasattr(self, "_camera"):
            raise RuntimeError("Hitbox not bound to spatial component and camera")

    @abstractmethod
    def contains_point(self, point: tuple[float, float]) -> bool:
        """Return True if the point is inside the hitbox."""
        ...

    @abstractmethod
    def draw(
        self, surface: pygame.Surface, color: tuple[int, int, int] = (255, 0, 0)
    ) -> None:
        """Draw the hitbox for debugging purposes."""
        ...


class RectangleHitbox(Hitbox):

    def contains_point(self, point: tuple[float, float]) -> bool:
        self._require_bind()
        result: bool = self._spatial_component.get_screen_rect(
            self._camera
        ).collidepoint(point)
        return result

    def draw(
        self, surface: pygame.Surface, color: tuple[int, int, int] = (0, 0, 255)
    ) -> None:
        self._require_bind()
        pygame.draw.rect(
            surface, color, self._spatial_component.get_screen_rect(self._camera), 1
        )


class EllipseHitbox(Hitbox):
    def contains_point(self, point: tuple[float, float]) -> bool:
        self._require_bind()
        rect = self._spatial_component.get_screen_rect(self._camera)

        # Compute ellipse center and radii
        cx = rect.x + rect.width / 2
        cy = rect.y + rect.height / 2
        rx = rect.width / 2
        ry = rect.height / 2

        px, py = point
        # Ellipse equation
        return ((px - cx) ** 2) / (rx**2) + ((py - cy) ** 2) / (ry**2) <= 1

    def draw(
        self, surface: pygame.Surface, color: tuple[int, int, int] = (0, 255, 0)
    ) -> None:
        self._require_bind()
        rect = self._spatial_component.get_screen_rect(self._camera)

        # Draw ellipse matching rect
        pygame.draw.ellipse(surface, color, rect, 1)


# TODO: could change this to polygonal hitbox and move all hex related functions to hexagon.
# TODO: don't forget to re-implement move_to_center
class HexHitbox(Hitbox):
    def _compute_points(
        self, rect: pygame.Rect | pygame.FRect
    ) -> list[tuple[float, float]]:
        """Compute hex points from the bounding rect."""
        cx = rect.x + rect.width / 2
        cy = rect.y + rect.height / 2
        w, h = rect.width / 2, rect.height / 2
        return [
            (cx, cy - h),  # top
            (cx + w, cy - h / 2),  # top-right
            (cx + w, cy + h / 2),  # bottom-right
            (cx, cy + h),  # bottom
            (cx - w, cy + h / 2),  # bottom-left
            (cx - w, cy - h / 2),  # top-left
        ]

    def contains_point(self, point: tuple[float, float]) -> bool:
        self._require_bind()
        rect = self._spatial_component.get_screen_rect(self._camera)
        points = self._compute_points(rect)

        # Ray-casting for convex polygon
        x, y = point
        inside = False
        n = len(points)
        for i in range(n):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % n]
            if (y1 > y) != (y2 > y):
                slope = (x2 - x1) * (y - y1) / (y2 - y1 + 1e-6) + x1  # avoid div0
                if x < slope:
                    inside = not inside
        return inside

    def draw(
        self, surface: pygame.Surface, color: tuple[int, int, int] = (0, 0, 255)
    ) -> None:
        self._require_bind()
        rect = self._spatial_component.get_screen_rect(self._camera)
        points = self._compute_points(rect)
        pygame.draw.polygon(surface, color, points, 1)
