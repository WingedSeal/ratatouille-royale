from pygame_gui.core.ui_element import UIElement
import pygame
from .spritesheet_structure import SpritesheetComponent
from ..anim.core.anim_structure import SequentialAnim, GroupedAnim, AnimEvent
from ratroyale.frontend.pages.page_elements.spatial_component import (
    Camera,
    SpatialComponent,
)
from ...pages.page_elements.hitbox import Hitbox


class VisualComponent:
    """Base class for anything that can be rendered as part of an Element.
    The visual component does not need to have a reference to the element itself.
    The element manager + register form layer will orchestrate the relationship.
    The positioning of the visual component inherits from the element it is related to.
    """

    def __init__(
        self,
        spritesheet_component: SpritesheetComponent | None = None,
        starting_anim: str | None = None,
    ) -> None:
        self._default_animation: SequentialAnim | None = None
        self._override_animation_queue: list[SequentialAnim] = []

        self.highlighted: bool = False
        self.spritesheet_component: SpritesheetComponent | None = spritesheet_component

        if self.spritesheet_component and starting_anim:
            self.spritesheet_component.set_frame(starting_anim, 0)

    def _bind(self, spatial_component: SpatialComponent, camera: Camera) -> None:
        self._spatial_component = spatial_component
        self._camera = camera

    def on_create(self) -> None:
        """Placeholder on create"""
        pass

    def on_destroy(self) -> None:
        """Used for triggering the .kill() on pygame_gui elements"""
        pass

    def animate(self, time: float) -> None:
        if self._override_animation_queue:
            animation_sequence = self._override_animation_queue[0]
            if animation_sequence.is_finished() and not animation_sequence.persistent:
                self._override_animation_queue.pop(0)
                return
        elif self._default_animation:
            animation_sequence = self._default_animation
        else:
            return

        if animation_sequence:
            animation_sequence.update(time)

    def _get_animation(self) -> GroupedAnim | None:
        if self._override_animation_queue:
            animation = self._override_animation_queue[0]
        elif self._default_animation:
            animation = self._default_animation
        else:
            return None

        return animation.get_animation_group()

    def render(
        self,
        interactable_comp: UIElement | Hitbox | None,
        spatial_comp: SpatialComponent,
        surface: pygame.Surface,
        camera: Camera,
    ) -> None:
        """Draw this visual onto the given surface."""
        spatial_rect = spatial_comp.get_screen_rect(camera)
        if isinstance(interactable_comp, UIElement):
            gui_rect = interactable_comp.get_relative_rect()
            if spatial_rect.size != gui_rect.size:
                # Only rebuild if size has changed. This is an attempt to reduce expensive rebuild calls.
                interactable_comp.set_dimensions(spatial_rect.size)
                interactable_comp.rebuild()  # type: ignore
            if spatial_rect.topleft != gui_rect.topleft:
                interactable_comp.set_relative_position(spatial_rect.topleft)
        else:
            if self.spritesheet_component:
                frame = self.spritesheet_component.output_frame(
                    spatial_rect, self._camera
                )
                if frame:
                    surface.blit(frame, spatial_rect.topleft)

        pygame.draw.rect(surface, (255, 0, 0), spatial_rect, width=2)

    def set_highlighted(self, highlighted: bool) -> None:
        """Set whether this visual is highlighted (e.g. selected)"""
        self.highlighted = highlighted

    def _to_sequential(
        self, animation: SequentialAnim | GroupedAnim | AnimEvent
    ) -> SequentialAnim:
        match animation:
            case SequentialAnim():
                return animation
            case GroupedAnim():
                return SequentialAnim(sequential_list=[animation])
            case AnimEvent():
                return SequentialAnim(
                    sequential_list=[GroupedAnim(group_list=[animation])]
                )
            case _:
                raise TypeError("The provided anim object is an incorrect type.")

    def set_default_animation(
        self, default_sequence: SequentialAnim | GroupedAnim | AnimEvent
    ) -> None:
        self._default_animation = self._to_sequential(default_sequence)

    def queue_override_animation(
        self, overriding_sequence: SequentialAnim | GroupedAnim | AnimEvent
    ) -> None:
        if (
            isinstance(overriding_sequence, SequentialAnim)
            and overriding_sequence.interrupts_queue
        ):
            self._override_animation_queue.clear()

        self._override_animation_queue.append(self._to_sequential(overriding_sequence))
