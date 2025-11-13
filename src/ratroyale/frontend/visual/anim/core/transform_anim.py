from dataclasses import dataclass

from ratroyale.frontend.pages.page_elements.spatial_component import (
    Camera,
    SpatialComponent,
)

from .anim_settings import (
    AnimDirection,
    HorizontalAnchor,
    MoveAnimMode,
    ScaleMode,
    SkewMode,
    VerticalAnchor,
)
from .anim_structure import AnimEvent


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
        self._start_pos: tuple[float, float] | None = None
        self._current_pos: tuple[float, float] | None = None

    def update(self, time_delta: float) -> None:
        eased_t = self.get_normalized_time(time_delta)
        if self._start_pos is None:
            _rect = self.spatial_component.get_rect()
            self._start_pos = (_rect.x, _rect.y)
            self._current_pos = self._start_pos
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
        rect = self.spatial_component.get_rect()
        self._start_size = rect.size

    def update(self, time_delta: float) -> None:
        eased_t = self.get_normalized_time(time_delta)

        # Use original start size
        start_width, start_height = self._start_size
        target_width, target_height = self.target

        # Compute new size
        if self.scale_mode == ScaleMode.SCALE_TO_SIZE:
            if self.reverse_pass_per_loop and self._direction is AnimDirection.REVERSE:
                new_width = start_width + (target_width - start_width) * (1 - eased_t)
                new_height = start_height + (target_height - start_height) * (
                    1 - eased_t
                )
            else:
                new_width = start_width + (target_width - start_width) * eased_t
                new_height = start_height + (target_height - start_height) * eased_t

        elif self.scale_mode == ScaleMode.SCALE_BY_FACTOR:
            if self.reverse_pass_per_loop and self._direction is AnimDirection.REVERSE:
                new_width = start_width * (1 + (target_width - 1) * (1 - eased_t))
                new_height = start_height * (1 + (target_height - 1) * (1 - eased_t))
            else:
                new_width = start_width * (1 + (target_width - 1) * eased_t)
                new_height = start_height * (1 + (target_height - 1) * eased_t)

        # Clamp to small minimum to avoid division by zero
        new_width = max(new_width, 1.0)
        new_height = max(new_height, 1.0)

        # current_rect = current top-left + size
        curr_rect = self.spatial_component.get_rect()
        curr_width, curr_height = curr_rect.size

        # Compute the anchor position dynamically each frame
        anchor_x, anchor_y = curr_rect.centerx, curr_rect.centery
        if self.expansion_anchor[0] == VerticalAnchor.UPPER:
            anchor_y = curr_rect.top
        elif self.expansion_anchor[0] == VerticalAnchor.LOWER:
            anchor_y = curr_rect.bottom

        if self.expansion_anchor[1] == HorizontalAnchor.LEFT:
            anchor_x = curr_rect.left
        elif self.expansion_anchor[1] == HorizontalAnchor.RIGHT:
            anchor_x = curr_rect.right

        # Top-left = anchor minus proportional offset from anchor to current top-left
        offset_x = anchor_x - curr_rect.x
        offset_y = anchor_y - curr_rect.y
        new_x = anchor_x - offset_x * (new_width / curr_width)
        new_y = anchor_y - offset_y * (new_height / curr_height)

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
