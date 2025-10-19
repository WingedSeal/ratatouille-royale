from dataclasses import dataclass
from .anim_structure import AnimEvent
from ratroyale.frontend.pages.page_elements.spatial_component import (
    SpatialComponent,
    Camera,
)
from .anim_settings import (
    MoveAnimMode,
    ScaleMode,
    SkewMode,
    HorizontalAnchor,
    VerticalAnchor,
    AnimDirection,
)


@dataclass(kw_only=True)
class TransformAnim(AnimEvent):
    spatial_component: SpatialComponent
    camera: Camera
    align_hitbox_during_anim: bool = True

    def align_hitbox(self) -> None:
        # TODO: use some sort of message to notify page to resize hitbox accordingly
        pass


@dataclass
class MoveAnim(TransformAnim):
    move_mode: MoveAnimMode
    direction_vector: tuple[float, float]

    def __post_init__(self) -> None:
        super().__post_init__()
        # Track starting position for interpolation
        # Get untransformed rect
        _rect = self.spatial_component.get_rect()
        self._start_pos: tuple[float, float] = (_rect.x, _rect.y)
        self._current_pos: tuple[float, float] = self._start_pos

    def update(self, time_delta: float) -> None:
        eased_t = self.get_normalized_time(time_delta)
        start_x, start_y = self._start_pos
        dx, dy = self.direction_vector

        if self.move_mode == MoveAnimMode.MOVE_BY:
            eased_t = (
                (1 - eased_t)
                if (
                    self.reverse_pass_per_loop
                    and self._direction is AnimDirection.REVERSE
                )
                else eased_t
            )
            new_x = start_x + dx * eased_t
            new_y = start_y + dy * eased_t

        elif self.move_mode == MoveAnimMode.MOVE_TO:
            target_x, target_y = dx, dy
            if self.reverse_pass_per_loop and self._direction is AnimDirection.REVERSE:
                new_x = target_x + (start_x - target_x) * eased_t
                new_y = target_y + (start_y - target_y) * eased_t
            else:
                new_x = start_x + (target_x - start_x) * eased_t
                new_y = start_y + (target_y - start_y) * eased_t

        else:
            raise ValueError(f"Unknown move_mode: {self.move_mode}")

        new_pos = (new_x, new_y)
        self.spatial_component.set_position(new_pos)

        if self.align_hitbox_during_anim:
            self.align_hitbox()


@dataclass
class ScaleAnim(TransformAnim):
    scale_mode: ScaleMode
    target: tuple[float, float]
    expansion_anchor: tuple[VerticalAnchor, HorizontalAnchor]

    def __post_init__(self) -> None:
        super().__post_init__()

        # Track starting position and size
        self._rect = self.spatial_component.get_rect().copy()
        self._start_size: tuple[float, float] = self._rect.size
        self._current_size: tuple[float, float] = self._start_size

        # Compute the anchor point based on expansion_anchor
        anchor_x, anchor_y = self._rect.x, self._rect.y  # default: top-left

        # Vertical anchor
        if self.expansion_anchor[0] == VerticalAnchor.MIDDLE:
            anchor_y = self._rect.centery
        elif self.expansion_anchor[0] == VerticalAnchor.LOWER:
            anchor_y = self._rect.bottom
        # else UPPER: keep as _rect.y

        # Horizontal anchor
        if self.expansion_anchor[1] == HorizontalAnchor.MIDDLE:
            anchor_x = self._rect.centerx
        elif self.expansion_anchor[1] == HorizontalAnchor.RIGHT:
            anchor_x = self._rect.right
        # else LEFT: keep as _rect.x

        self._anchor_pos: tuple[float, float] = (anchor_x, anchor_y)

    def update(self, time_delta: float) -> None:
        # Get normalized time (0–1) according to easing and loop logic
        eased_t = self.get_normalized_time(time_delta)

        start_width, start_height = self._start_size
        target_width, target_height = self.target

        # Compute new size
        if self.scale_mode == ScaleMode.SCALE_TO_SIZE:
            if self.reverse_pass_per_loop and self._direction is AnimDirection.REVERSE:
                # Interpolate from target back to start
                new_width = target_width + (start_width - target_width) * eased_t
                new_height = target_height + (start_height - target_height) * eased_t
            else:
                # Interpolate from start to target
                new_width = start_width + (target_width - start_width) * eased_t
                new_height = start_height + (target_height - start_height) * eased_t

        elif self.scale_mode == ScaleMode.SCALE_BY_FACTOR:
            if self.reverse_pass_per_loop and self._direction is AnimDirection.REVERSE:
                # Scale back down toward original size
                new_width = start_width * (target_width - (target_width - 1) * eased_t)
                new_height = start_height * (
                    target_height - (target_height - 1) * eased_t
                )
            else:
                # Scale up by factor
                new_width = start_width * (1 + (target_width - 1) * eased_t)
                new_height = start_height * (1 + (target_height - 1) * eased_t)

        else:
            raise ValueError(f"Unknown scale_mode: {self.scale_mode}")

        # Anchor-aware position
        anchor_x, anchor_y = self._anchor_pos
        new_x = anchor_x - (anchor_x - self._rect.x) * (new_width / self._start_size[0])
        new_y = anchor_y - (anchor_y - self._rect.y) * (
            new_height / self._start_size[1]
        )

        # Apply new size and position
        self.spatial_component.set_position((new_x, new_y))
        self.spatial_component.set_size((new_width, new_height))

        if self.align_hitbox_during_anim:
            self.align_hitbox()


@dataclass
class RotateAnim(TransformAnim):
    """This will have no effect on pygame GUI elements (neither visual nor hitbox will change). Mainly used to rotate sprite images.
    Positive angle is clockwise rotation, while negative is counterclockwise."""

    angle: float
    pivot: tuple[VerticalAnchor, HorizontalAnchor] = (
        VerticalAnchor.MIDDLE,
        HorizontalAnchor.MIDDLE,
    )


@dataclass
class SkewAnim(TransformAnim):
    """Unused"""

    skew_mode: SkewMode
    target: tuple[float, float]
    pivot: tuple[VerticalAnchor, HorizontalAnchor] = (
        VerticalAnchor.MIDDLE,
        HorizontalAnchor.MIDDLE,
    )
