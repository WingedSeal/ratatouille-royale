from ..core.overlay_anim import ColorOverlayAnim
from ..core.anim_structure import SequentialAnim, GroupedAnim
from ..core.transform_anim import ScaleAnim, MoveAnim
from ..core.sprite_anim import SpriteAnim
from ..core.anim_settings import (
    TimingMode,
    ScaleMode,
    VerticalAnchor,
    HorizontalAnchor,
    MoveAnimMode,
)
from ...asset_management.spritesheet_structure import SpritesheetComponent
from ....pages.page_elements.spatial_component import SpatialComponent, Camera

import pytweening  # type: ignore
import pygame


def on_select_color_fade_in(
    spritesheet_component: SpritesheetComponent, color: pygame.Color
) -> SequentialAnim:
    color_overlay_anim = ColorOverlayAnim(
        spritesheet_component=spritesheet_component,
        pygame_blend_mode=pygame.BLEND_RGB_ADD,
        intensity_range=(0.0, 0.5),
        color=color,
        timing_mode=TimingMode.DURATION_PER_LOOP,
        period_in_seconds=0.15,
    )
    result = SequentialAnim(
        [GroupedAnim([color_overlay_anim], run_together_with_default=True)],
        interrupts_queue=True,
    )
    return result


def on_select_color_fade_out(
    spritesheet_component: SpritesheetComponent, color: pygame.Color
) -> SequentialAnim:
    color_overlay_anim = ColorOverlayAnim(
        spritesheet_component=spritesheet_component,
        pygame_blend_mode=pygame.BLEND_RGB_ADD,
        intensity_range=(0.5, 0),
        color=color,
        timing_mode=TimingMode.DURATION_PER_LOOP,
        period_in_seconds=0.15,
    )
    result = SequentialAnim(
        [GroupedAnim([color_overlay_anim], run_together_with_default=True)],
        interrupts_queue=True,
    )
    return result


def shrink_squeak(
    spatial_component: SpatialComponent, camera: Camera
) -> SequentialAnim:
    scale_anim = ScaleAnim(
        easing_func=pytweening.easeOutCirc,
        timing_mode=TimingMode.DURATION_PER_LOOP,
        period_in_seconds=0.2,
        spatial_component=spatial_component,
        camera=camera,
        scale_mode=ScaleMode.SCALE_BY_FACTOR,
        target=(0.5, 0.5),
        expansion_anchor=(VerticalAnchor.MIDDLE, HorizontalAnchor.MIDDLE),
    )
    result = SequentialAnim([GroupedAnim([scale_anim])], interrupts_queue=True)
    return result


def return_squeak_to_normal(
    spatial_component: SpatialComponent,
    camera: Camera,
    direction_vector: tuple[float, float],
    target_size: tuple[int, int],
) -> SequentialAnim:
    scale_anim = ScaleAnim(
        easing_func=pytweening.easeOutCirc,
        timing_mode=TimingMode.DURATION_PER_LOOP,
        period_in_seconds=0.2,
        spatial_component=spatial_component,
        camera=camera,
        scale_mode=ScaleMode.SCALE_TO_SIZE,
        target=target_size,
        expansion_anchor=(VerticalAnchor.MIDDLE, HorizontalAnchor.MIDDLE),
    )
    move_anim = MoveAnim(
        easing_func=pytweening.easeOutCirc,
        timing_mode=TimingMode.DURATION_PER_LOOP,
        period_in_seconds=0.2,
        spatial_component=spatial_component,
        camera=camera,
        move_mode=MoveAnimMode.MOVE_TO,
        direction_vector=direction_vector,
    )
    result = SequentialAnim(
        [GroupedAnim([scale_anim, move_anim])], interrupts_queue=True
    )
    return result


def default_idle_for_entity(
    spritesheet_component: SpritesheetComponent,
) -> SequentialAnim:
    sprite_anim = SpriteAnim(
        spritesheet_component=spritesheet_component,
        animation_name="IDLE",
        timing_mode=TimingMode.DURATION_PER_LOOP,
        period_in_seconds=0.5,
    )
    result = SequentialAnim([GroupedAnim([sprite_anim])], interrupts_queue=True)
    return result


def move_entity(
    target_pos: tuple[float, float],
    spatial: SpatialComponent,
    camera: Camera,
) -> SequentialAnim:
    move_anim = MoveAnim(
        move_mode=MoveAnimMode.MOVE_TO,
        direction_vector=target_pos,
        easing_func=pytweening.easeOutExpo,
        timing_mode=TimingMode.DURATION_PER_LOOP,
        spatial_component=spatial,
        camera=camera,
        period_in_seconds=0.25,
        callback="FINISHED",
    )
    result = SequentialAnim(
        [GroupedAnim([move_anim], run_together_with_default=True)],
        interrupts_queue=False,
    )
    return result
