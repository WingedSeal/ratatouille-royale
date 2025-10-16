import pygame

from ratroyale.event_tokens.input_token import InputManagerEvent, post_gesture_event
from ratroyale.frontend.gesture.gesture_data import GestureData
from ratroyale.frontend.visual.asset_management.visual_component import VisualComponent
from typing import TypeVar
from pygame_gui.core import UIElement
from ratroyale.event_tokens.payloads import Payload
from .spatial_component import SpatialComponent, Camera
from .hitbox import Hitbox

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
    ) -> None:
        # Identification info
        self.registered_name: str = registered_name
        self.grouping_name: str = grouping_name

        # Spatial info
        self.spatial_component: SpatialComponent = spatial_component

        # Hierachical info
        self.parent: ElementWrapper | None = None
        self.children: list[ElementWrapper] = []

        # Interactivity info
        self.interactable_component: UIElement | Hitbox | None = interactable_component
        self.payload: Payload | None = payload
        self.is_blocking: bool = is_blocking

        # Visual info
        self.visual_component: VisualComponent | None = visual_component

        self.camera: Camera = camera

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

    def handle_gesture(
        self, gesture: GestureData, is_processing_input: bool, camera: Camera
    ) -> bool:
        if not isinstance(self.interactable_component, Hitbox):
            return False

        if not is_processing_input:
            return False

        pos = gesture.mouse_pos
        if pos is None or not self.interactable_component.contains_point(pos):
            return False

        post_gesture_event(
            InputManagerEvent(
                element_id=self.registered_name,
                gesture_data=gesture,
                payload=self.payload,
            )
        )

        return self.is_blocking

    def destroy(self) -> None:
        if isinstance(self.interactable_component, UIElement):
            self.interactable_component.kill()  # type: ignore

    def set_position(self, topleft: tuple[float, float]) -> None:
        """Move this interactable and reposition all children accordingly."""
        self.spatial_component.set_position(topleft)

        for child in self.children:
            self._align_child(child)

    def _align_child(self, child: "ElementWrapper") -> None:
        parent_x = self.spatial_component.local_rect.x
        parent_y = self.spatial_component.local_rect.y
        child_x = parent_x + child.spatial_component.local_rect.x
        child_y = parent_y + child.spatial_component.local_rect.y
        child.spatial_component.set_position((child_x, child_y))

    def add_child(self, child: "ElementWrapper") -> None:
        if child in self.children:
            raise ValueError(
                f"Child '{child.registered_name}' already attached to '{self.registered_name}'"
            )

        self.children.append(child)
        child.parent = self
        self._align_child(child)

    def remove_child(self, child: "ElementWrapper") -> None:
        if child not in self.children:
            raise ValueError(
                f"Child '{child.registered_name}' not found in '{self.registered_name}'"
            )
        self.children.remove(child)
        child.parent = None

    def render(self, surface: pygame.Surface) -> None:
        if self.visual_component:
            self.visual_component.render(
                self.interactable_component,
                self.spatial_component,
                surface,
                self.camera,
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
        for child in self.children:
            child.draw_hitbox(surface, color)


def ui_element_wrapper(
    element: UIElement,
    registered_name: str,
    camera: Camera,
    grouping_name: str = "UI_ELEMENT",
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
    spatial = SpatialComponent(rect)

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
