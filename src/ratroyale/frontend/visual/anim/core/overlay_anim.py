from dataclasses import dataclass
from typing import Literal
import pygame
from .anim_structure import AnimEvent
from ...asset_management.spritesheet_structure import SpritesheetComponent


@dataclass
class OverlayAnim(AnimEvent):
    spritesheet_component: SpritesheetComponent
    blend_mode: int  # for pygame blend modes
    intensity_range: tuple[float, float]


@dataclass
class ColorOverlayAnim(OverlayAnim):
    color: pygame.Color

    def __post_init__(self) -> None:
        super().__post_init__()

        self._current_intensity = 0.0

    def update(self, dt: float) -> None:
        """Update overlay intensity (alpha) over time."""
        eased_t = self.get_normalized_time(dt)

        # Reverse phase for ping-pong
        if self.reverse_pass_per_loop and self._direction < 0:
            eased_t = 1.0 - eased_t

        # Interpolate overlay intensity (0–1)
        min_intensity, max_intensity = self.intensity_range
        intensity = min_intensity + (max_intensity - min_intensity) * eased_t
        self._current_intensity = intensity

        # Compute current overlay color (same RGB, variable alpha)
        r, g, b = self.color.r, self.color.g, self.color.b
        a = int(self.color.a * intensity)
        overlay_color = pygame.Color(r, g, b, a)

        # Apply to visual component
        self.spritesheet_component.set_overlay(overlay_color, self.blend_mode)

        return None


@dataclass
class ImageOverlayAnim(OverlayAnim):
    image: pygame.Surface


@dataclass
class FadeOverlayAnim(OverlayAnim):
    start_alpha: int
    end_alpha: int
