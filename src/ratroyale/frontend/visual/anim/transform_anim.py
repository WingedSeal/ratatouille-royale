from dataclasses import dataclass
from typing import Literal
import pygame
from .anim_structure import AnimEvent

MoveAnimMode = Literal["MOVE_TO", "MOVE_BY"]
ScaleMode = Literal["SCALE_TO_SIZE", "SCALE_BY_FACTOR"]
HorizontalAnchor = Literal["LEFT", "MIDDLE", "RIGHT"]
VerticalAnchor = Literal["UPPER", "MIDDLE", "LOWER"]
SkewMode = Literal["SKEW_TO", "SKEW_BY"]
"""SKEW_TO: animates towards a target skew value
SKEW_BY: animates relative to the current skew value"""


@dataclass
class TransformAnim(AnimEvent):
    align_hitbox_during: bool
    align_hitbox_on_ending: bool


@dataclass
class MoveAnim(TransformAnim):
    move_mode: MoveAnimMode
    direction_vector: tuple[float, float]


@dataclass
class ScaleAnim(TransformAnim):
    scale_mode: ScaleMode
    target: tuple[float, float]
    expansion_anchor: tuple[VerticalAnchor, HorizontalAnchor]


@dataclass
class RotateAnim(TransformAnim):
    angle: float
    pivot: tuple[VerticalAnchor, HorizontalAnchor] = ("MIDDLE", "MIDDLE")


@dataclass
class SkewAnim(TransformAnim):
    skew_mode: SkewMode
    target: tuple[float, float]
    pivot: tuple[VerticalAnchor, HorizontalAnchor] = ("MIDDLE", "MIDDLE")
