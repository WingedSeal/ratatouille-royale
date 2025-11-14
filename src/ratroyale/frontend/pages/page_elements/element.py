import pygame

from ratroyale.event_tokens.input_token import InputManagerEvent, post_gesture_event
from ratroyale.frontend.gesture.gesture_data import GestureData
from ratroyale.frontend.visual.asset_management.visual_component import VisualComponent
from typing import TypeVar
from pygame_gui.core import UIElement
from ratroyale.event_tokens.payloads import Payload
from .spatial_component import SpatialComponent, Camera
from .hitbox import Hitbox, RectangleHitbox
from ratroyale.frontend.visual.anim.core.anim_structure import (
    AnimEvent,
    SequentialAnim,
    GroupedAnim,
)
from ...visual.screen_constants import screen_rect

T = TypeVar("T")


class ElementWrapper:
    """
    Base class to wrap all components of a page element.
    A page element consists of three distinct components:\n
        SpatialComponent - dictates spatial information, including whether the element lives in world or screen space.
        InteractableComponent - dictates input & output. (optional)
        VisualComponent - dictates visuals & animations. (optional)
    """

    def __init__(
        self,
        registered_name: str,
        grouping_name: str,
        camera: Camera,
        spatial_component: SpatialComponent,
        interactable_component: UIElement | Hitbox | None = None,
        visual_component: VisualComponent | None = None,
        payload: Payload | None = None,
        is_blocking: bool = True,
        parent_element: str | None = None,
    ) -> None:
        # Identification info
        self.registered_name: str = registered_name
        self.grouping_name: str = grouping_name

        # Spatial info
        self.spatial_component: SpatialComponent = spatial_component

        # Hierachical info
        self.parent_element: str | None = parent_element
        self.parent: ElementWrapper | None = None
        self.children: dict[str, ElementWrapper] = {}

        # Interactivity info
        self.interactable_component: UIElement | Hitbox | None = interactable_component
        self.payload: Payload | None = payload
        self.is_blocking: bool = is_blocking
        self.is_interactable: bool = True
        self._supporting_hitbox_for_ui_elements: RectangleHitbox

        # Visual info
        self.visual_component: VisualComponent | None = visual_component

        self.camera: Camera = camera
        self._is_visible: bool = True
        """Cached visibility status"""

        if isinstance(self.interactable_component, Hitbox):
            self.interactable_component._bind(spatial_component, camera)

        if self.visual_component:
            self.visual_component._bind(spatial_component, camera)

    def get_interactable(self, cls: type[T]) -> T:
        if not self.interactable_component:
            raise AttributeError(
                "This element wrapper does not have an interactable component."
            )
        if not isinstance(self.interactable_component, cls):
            raise TypeError(
                f"The type provided {cls.__name__} was incorrect. The actual type was {type(self.interactable_component).__name__}"
            )
        else:
            return self.interactable_component

    def get_payload(self, cls: type[T]) -> T:
        if not self.payload:
            raise AttributeError("This element wrapper does not have a payload.")
        if not isinstance(self.payload, cls):
            raise TypeError(
                f"The element {self.registered_name} has payload type {type(self.payload).__name__}, not {cls.__name__}."
            )
        else:
            return self.payload

    def handle_gesture(self, gesture: GestureData, is_processing_input: bool) -> bool:
        # Filter out input non-processing scenarios.
        if not is_processing_input:
            return False

        if not self.is_interactable:
            return False

        # Detects input based on interactable component's type:
        pos = gesture.mouse_pos
        if isinstance(self.interactable_component, Hitbox):
            if self.interactable_component.contains_point(pos):
                post_gesture_event(
                    InputManagerEvent(
                        element_id=self.registered_name,
                        gesture_data=gesture,
                        payload=self.payload,
                    )
                )
                return self.is_blocking
            else:
                return False
        elif isinstance(self.interactable_component, UIElement):
            if self.get_absolute_rect().collidepoint(pos):
                return self.is_blocking
            else:
                return False
        else:
            return False

    def destroy(self) -> None:
        if isinstance(self.interactable_component, UIElement):
            self.interactable_component.kill()  # type: ignore

    def add_child(self, child: "ElementWrapper") -> None:
        if child.registered_name in self.children:
            raise ValueError(
                f"Child '{child.registered_name}' already attached to '{self.registered_name}'"
            )

        self.children[child.registered_name] = child
        child.parent = self

    def remove_child(self, child: "ElementWrapper") -> None:
        if child.registered_name not in self.children:
            raise ValueError(
                f"Child '{child.registered_name}' not found in '{self.registered_name}'"
            )
        self.children.pop(child.registered_name)
        child.parent = None

    def remove_child_by_name(self, child_name: str) -> None:
        if child_name not in self.children:
            raise ValueError(
                f"Child '{child_name}' not found in '{self.registered_name}'"
            )
        child = self.children.pop(child_name)
        child.parent = None

    # TODO: somethings wrong here
    def get_absolute_rect(self) -> pygame.Rect | pygame.FRect:
        self.spatial_component.invalidate_cache()

        if isinstance(self.interactable_component, UIElement):
            return self.interactable_component.get_abs_rect()

        if not self.parent:
            # No parent: just project to screen
            return self.spatial_component.get_screen_rect(self.camera).copy()

        # Get scaled child rect (top-left scaled, no position change)
        child_rect = self.spatial_component.get_relative_rect(self.camera).copy()

        # Get parent screen rect
        parent_rect = self.parent.spatial_component.get_screen_rect(self.camera)

        # Determine parent scale factor (combined element + camera scale)
        parent_scale = (
            self.parent.spatial_component.scale * self.camera.scale
            if self.parent.spatial_component.space_mode == "WORLD"
            else self.parent.spatial_component.scale
        )

        # Add scaled offset from parent
        child_rect.x += parent_rect.x
        child_rect.y += parent_rect.y

        # Offset respect scale of parent
        child_rect.x += self.spatial_component.local_rect.x * (parent_scale - 1)
        child_rect.y += self.spatial_component.local_rect.y * (parent_scale - 1)

        return child_rect

    def render(self, surface: pygame.Surface) -> None:
        # Only recompute visibility if camera moved
        if self.camera._dirty:
            self.update_visibility()

        # Skip entirely if not visible
        if not self._is_visible:
            return

        abs_rect = self.get_absolute_rect()
        if self.visual_component:
            self.visual_component.render(
                self.interactable_component,
                abs_rect,
                surface,
            )

        # DRAW RECT DEBUG
        # pygame.draw.rect(surface, (255, 0, 0), abs_rect, width=2)

    def update_visibility(self) -> None:
        """Recompute visibility only if camera is dirty or element moved."""
        spatial = self.get_absolute_rect()
        if spatial:
            self._is_visible = spatial.colliderect(screen_rect)
        else:
            self._is_visible = False

    def queue_override_animation(
        self, anim_event: AnimEvent | SequentialAnim | GroupedAnim
    ) -> None:
        if self.visual_component:
            self.visual_component.queue_override_animation(anim_event)
        else:
            raise AttributeError(
                "This element wrapper does not have a visual component."
            )

    def set_default_animation(
        self, anim_event: AnimEvent | SequentialAnim | GroupedAnim
    ) -> None:
        if self.visual_component:
            self.visual_component.set_default_animation(anim_event)
        else:
            raise AttributeError(
                "This element wrapper does not have a visual component."
            )

    # --- Debug Utility ---
    def draw_hitbox(
        self, surface: pygame.Surface, color: tuple[int, int, int] = (255, 0, 0)
    ) -> None:
        """Draw this interactable's hitbox and its children's recursively."""
        if not self.interactable_component or isinstance(
            self.interactable_component, UIElement
        ):
            return

        self.interactable_component.draw(surface, color)
        for child in self.children.values():
            child.draw_hitbox(surface, color)

    def on_select(self) -> bool:
        return False

    def on_deselect(self) -> bool:
        return False

    def on_highlight(self) -> bool:
        return False

    def on_unhighlight(self) -> bool:
        return False

    def get_registered_name(self) -> str:
        return self.registered_name

    def get_grouping_name(self) -> str:
        return self.grouping_name


def ui_element_wrapper(
    element: UIElement,
    registered_name: str,
    camera: Camera,
    grouping_name: str = "UI_ELEMENT",
    z_order: int = 1,
) -> ElementWrapper:
    """
    Convenience helper to wrap a pygame_gui element into an ElementWrapper.

    Args:
        element: The pygame_gui element to wrap (e.g., UIButton, UILabel, etc.)
        registered_name: The internal name to register the element with.
        grouping_name: Optional grouping category for organization.
        camera: Optional camera reference if this element participates in world-space transforms.

    Returns:
        ElementWrapper: A fully constructed wrapper containing spatial, visual, and interactable components.
    """
    # Get its current rect from pygame_gui
    rect = element.relative_rect

    # Build the spatial component using the element's rect
    spatial = SpatialComponent(rect, z_order=z_order)

    # Build the visual and interactable components
    visual = VisualComponent()
    interactable = element  # pygame_gui element itself acts as interactable

    # Return the wrapper
    return ElementWrapper(
        registered_name=registered_name,
        grouping_name=grouping_name,
        camera=camera,
        spatial_component=spatial,
        visual_component=visual,
        interactable_component=interactable,
    )
