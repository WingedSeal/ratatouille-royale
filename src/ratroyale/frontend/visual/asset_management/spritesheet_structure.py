from dataclasses import dataclass, field
import pygame
from .spritesheet_manager import SpritesheetManager
from ratroyale.frontend.pages.page_elements.spatial_component import Camera


@dataclass
class SpritesheetComponent:
    """Used in custom elements to hold metadata for drawing."""

    spritesheet_reference: str | pygame.Surface
    """Can either hold a spritesheet reference or a raw surface for drawing."""
    _scale_cache: dict[tuple[int, int | float, int | float], pygame.Surface] = field(
        default_factory=dict
    )
    _rounded_corner: int | None = None
    """Caches image scale to reduce pygame.transform.scale calls"""

    def __post_init__(self) -> None:
        self._current_anim_name: str | None = None
        self._current_anim_frame_index: int | None = None
        self._overlay_color: pygame.Color | None = None
        self._overlay_mode: int = 0
        self._overlay_surface: pygame.Surface | None = None
        self._overlay_persistence: bool = True

        self.set_frame("IDLE", 0)

    def set_frame(self, current_anim_name: str, current_anim_frame_index: int) -> None:
        self._current_anim_name = current_anim_name
        self._current_anim_frame_index = current_anim_frame_index

    def _fit_with_spatial_rect(
        self, current_frame: pygame.Surface, target_rect: pygame.Rect | pygame.FRect
    ) -> pygame.Surface:
        """
        Scale frame exactly to target rect size (ignore camera scale)
        and optionally apply rounded corners if self._rounded_corner is set.
        """
        target_w, target_h = target_rect.size
        frame_id = id(current_frame)
        key = (frame_id, target_w, target_h)

        if key in self._scale_cache:
            return self._scale_cache[key]

        # Ensure 32-bit with alpha
        surf = current_frame.convert_alpha()
        scaled_frame = pygame.transform.smoothscale(surf, (target_w, target_h))

        # Prepare final surface
        aligned_surface = pygame.Surface((target_w, target_h), pygame.SRCALPHA)
        aligned_surface.blit(scaled_frame, (0, 0))

        # Apply rounded corners if requested
        if self._rounded_corner is not None and self._rounded_corner > 0:
            mask = pygame.Surface((target_w, target_h), pygame.SRCALPHA)
            pygame.draw.rect(
                mask,
                (255, 255, 255, 255),
                mask.get_rect(),
                border_radius=self._rounded_corner,
            )
            # Multiply mask onto aligned surface
            aligned_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Cache and return
        self._scale_cache[key] = aligned_surface
        return aligned_surface

    def _current_frame(self) -> pygame.Surface:
        if isinstance(self.spritesheet_reference, str):
            spritesheet = SpritesheetManager.get_spritesheet(self.spritesheet_reference)
            if self._current_anim_name and self._current_anim_frame_index is not None:
                return spritesheet.get_sprite_by_name(
                    self._current_anim_name, self._current_anim_frame_index
                )
            else:
                raise AttributeError(
                    "Either anim name or anim frame index was not set."
                )
        else:
            return self.spritesheet_reference

    # region Overlay Support

    def set_overlay(self, color: pygame.Color, blend_mode: int = 0) -> None:
        """Set the overlay color and blend mode to apply during rendering."""
        self._overlay_color = color
        self._overlay_mode = blend_mode

    def _apply_overlay(self, current_frame: pygame.Surface) -> pygame.Surface:
        if self._overlay_color is None:
            return current_frame

        # Lazy-create overlay surface
        if (
            self._overlay_surface is None
            or self._overlay_surface.get_size() != current_frame.get_size()
        ):
            self._overlay_surface = pygame.Surface(
                current_frame.get_size(), pygame.SRCALPHA
            )

        self._overlay_surface.fill(self._overlay_color)

        # Blend according to mode
        tinted = current_frame.copy()
        if not self._overlay_mode:
            tinted.blit(self._overlay_surface, (0, 0))
        else:
            tinted.blit(self._overlay_surface, (0, 0), special_flags=self._overlay_mode)

        return tinted

    # endregion

    def output_frame(
        self, spatial_rect: pygame.Rect | pygame.FRect, camera: Camera
    ) -> pygame.Surface:
        current_frame = self._current_frame()
        aligned = self._fit_with_spatial_rect(current_frame, spatial_rect)
        overlaid = self._apply_overlay(aligned)

        return overlaid
