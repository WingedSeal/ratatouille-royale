from abc import ABC, abstractmethod
from typing import Any

import pygame

from ratroyale.event_tokens.input_token import InputManagerEvent, post_gesture_event
from ratroyale.frontend.gesture.gesture_data import GestureData
from ratroyale.frontend.visual.asset_management.visual_component import VisualComponent

# region Hitbox Classes


class Hitbox(ABC):
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

    @abstractmethod
    def set_position(self, topleft_coord: tuple[float, float]) -> None:
        """Move the hitbox to a new topleft coordinate"""
        ...

    @abstractmethod
    def get_topleft(self) -> tuple[float, float]:
        """Returns the rectangular top-left coord, no matter the shape of the actual hitbox."""
        ...

    @abstractmethod
    def get_size(self) -> tuple[float, float]:
        """Returns the rectangular bounding box's size, no matter the shape of the actual hitbox."""
        ...


class RectangleHitbox(Hitbox):
    def __init__(self, rect: tuple[float, float, float, float]) -> None:
        self.rect: pygame.Rect = pygame.Rect(rect)

    def contains_point(self, point: tuple[float, float]) -> bool:
        result: bool = self.rect.collidepoint(point)
        return result

    def draw(
        self, surface: pygame.Surface, color: tuple[int, int, int] = (0, 0, 255)
    ) -> None:
        pygame.draw.rect(surface, color, self.rect, 1)

    def set_position(self, topleft_coord: tuple[float, float]) -> None:
        self.rect.topleft = topleft_coord

    def get_topleft(self) -> tuple[float, float]:
        result: tuple[float, float] = self.rect.topleft
        return result

    def get_size(self) -> tuple[float, float]:
        result: tuple[float, float] = self.rect.size
        return result


class CircleHitbox(Hitbox):
    def __init__(self, center: tuple[float, float], radius: int) -> None:
        self.center = center
        self.radius = radius

    def contains_point(self, point: tuple[float, float]) -> bool:
        x, y = point
        cx, cy = self.center
        return (x - cx) ** 2 + (y - cy) ** 2 <= self.radius**2

    def draw(
        self, surface: pygame.Surface, color: tuple[int, int, int] = (0, 255, 0)
    ) -> None:
        pygame.draw.circle(surface, color, self.center, self.radius, 1)

    def set_position(self, topleft_coord: tuple[float, float]) -> None: ...

    def get_topleft(self) -> tuple[float, float]:
        return (self.center[0] - self.radius, self.center[1] + self.radius)

    def get_size(self) -> tuple[float, float]:
        return (2 * self.radius, 2 * self.radius)


# TODO: could change this to polygonal hitbox and move all hex related functions to hexagon.py
class HexHitbox(Hitbox):
    def __init__(self, rect: tuple[float, float, float, float]) -> None:
        """
        topleft: (x, y) of the top-left bounding box of the hex
        width: corner-to-corner horizontally
        height: point-to-point vertically
        """
        self.topleft = (rect[0], rect[1])
        self.width = rect[2]
        self.height = rect[3]
        # Convert top-left to center
        cx = self.topleft[0] + self.width / 2
        cy = self.topleft[1] + self.height / 2
        self.move_to_center((cx, cy))

    def _compute_points(self, center: tuple[float, float]) -> list[tuple[float, float]]:
        cx, cy = center
        w, h = self.width / 2, self.height / 2
        return [
            (cx, cy - h),  # top
            (cx + w, cy - h / 2),  # top-right
            (cx + w, cy + h / 2),  # bottom-right
            (cx, cy + h),  # bottom
            (cx - w, cy + h / 2),  # bottom-left
            (cx - w, cy - h / 2),  # top-left
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

    def set_position(self, topleft_coord: tuple[float, float]) -> None:
        """Move the hitbox so that the top-left of its bounding box is at `topleft`."""
        cx = topleft_coord[0] + self.width / 2
        cy = topleft_coord[1] + self.height / 2
        self.move_to_center((cx, cy))

    def move_to_center(self, center: tuple[float, float]) -> None:
        """Move the hitbox so that its center is at `center`."""
        self.cx, self.cy = center
        self.points = self._compute_points(center)

    def draw(
        self, surface: pygame.Surface, color: tuple[int, int, int] = (0, 0, 255)
    ) -> None:
        pygame.draw.polygon(surface, color, self.points, 1)

    def get_topleft(self) -> tuple[float, float]:
        return self.topleft

    def get_size(self) -> tuple[float, float]:
        return (self.width, self.height)


# endregion

# region Base Element Class


class Element[T]():
    """
    Base class for a non-pygame_gui logical page element.
    Handles hitbox-based input detection and optional visual component.
    """

    def __init__(
        self,
        element_id: str,
        hitbox: Hitbox,
        payload: T | None = None,
        is_interactable: bool = True,
        is_blocking: bool = True,
        z_order: int = 0,
        visual: VisualComponent | None = None,
    ) -> None:
        self.element_id: str = element_id
        self.hitbox: Hitbox = hitbox
        self.payload: T | None = payload
        self.is_interactable: bool = is_interactable
        self.is_blocking: bool = is_blocking
        self._relative_offset: tuple[float, float] = (0, 0)  # Offset from parent if any

        self.z_order: int = z_order
        self.visual: VisualComponent | None = visual

        self.parent: Element[Any] | None = None
        self.children: list[Element[Any]] = []

    def handle_gesture(self, gesture: GestureData) -> bool:
        if not self.is_interactable:
            return False

        pos = gesture.mouse_pos
        if pos is None or not self.hitbox.contains_point(pos):
            return False

        post_gesture_event(
            InputManagerEvent(
                element_id=self.element_id,
                gesture_data=gesture,
                payload=self.payload,
            )
        )
        return True

    def destroy_visual(self) -> None:
        if self.visual:
            self.visual.destroy()

    def get_topleft(self) -> tuple[float, float]:
        """Return the current top-left position of this interactable."""
        return self.hitbox.get_topleft()

    def set_position(self, topleft: tuple[float, float]) -> None:
        """Move this interactable and reposition all children accordingly."""
        self.hitbox.set_position(topleft)
        if self.visual:
            self.visual.set_position(topleft)

        # Move children based on stored relative offsets
        for child in self.children:
            child_x = topleft[0] + child._relative_offset[0]
            child_y = topleft[1] + child._relative_offset[1]
            child.set_position((child_x, child_y))

    def add_position(self, delta: tuple[float, float]) -> None:
        new_pos = (self.get_topleft()[0] + delta[0], self.get_topleft()[1] + delta[1])
        self.set_position(new_pos)

    def add_child(
        self, child: "Element[Any]", offset: tuple[float, float] | None = None
    ) -> None:
        """
        Attach a child interactable.
        If offset is None, compute it from current absolute positions.
        """
        if child in self.children:
            raise ValueError(
                f"Child '{child.element_id}' already attached to '{self.element_id}'"
            )

        self.children.append(child)
        child.parent = self

        if offset is None:
            # Infer offset based on current positions
            px, py = self.get_topleft()
            cx, cy = child.get_topleft()
            offset = (cx - px, cy - py)

        child._relative_offset = offset
        self._update_child_position(child)

    def remove_child(self, child: "Element[Any]") -> None:
        """Detach a child interactable."""
        if child not in self.children:
            raise ValueError(
                f"Child '{child.element_id}' not found in '{self.element_id}'"
            )
        self.children.remove(child)
        child.parent = None
        child._relative_offset = (0, 0)

    def _update_child_position(self, child: "Element[Any]") -> None:
        """Reposition a specific child based on its stored offset."""
        parent_x, parent_y = self.get_topleft()
        offset_x, offset_y = child._relative_offset
        child.set_position((parent_x + offset_x, parent_y + offset_y))

    def render(self, surface: pygame.Surface) -> None:
        if self.visual:
            self.visual.render(surface)

    def get_size(self) -> tuple[float, float]:
        return self.hitbox.get_size()

    # --- Debug Utility ---
    def draw_hitbox(
        self, surface: pygame.Surface, color: tuple[int, int, int] = (255, 0, 0)
    ) -> None:
        """Draw this interactable's hitbox and its children's recursively."""
        self.hitbox.draw(surface, color)
        for child in self.children:
            child.draw_hitbox(surface, color)


# endregion
