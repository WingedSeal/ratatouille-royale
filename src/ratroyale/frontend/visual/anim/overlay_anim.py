from dataclasses import dataclass
from typing import Literal
import pygame
from .anim_structure import AnimEvent


BlendMode = Literal["BRIGHTEN", "DARKEN", "TINT", "HIGHLIGHT", "SHADOW"]
"""Each one corresponds to a different blend mode provided by pygame.\n
BRIGHTEN = addition\n
DARKEN = subtraction\n
TINT = multiplication\n
HIGHLIGHT = mask max\n
SHADOW = mask min
"""


@dataclass
class OverlayAnim(AnimEvent):
    blend_mode: BlendMode


@dataclass
class ColorOverlayAnim(AnimEvent):
    color: pygame.Color


@dataclass
class ImageOverlayAnim(AnimEvent):
    image: pygame.Surface
