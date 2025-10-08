from dataclasses import dataclass
from .base import EventToken
from ratroyale.frontend.visual.asset_management.visual_component import VisualComponent
from ratroyale.frontend.pages.page_elements.element import Element
from pygame_gui.ui_manager import UIManager
from ratroyale.backend.tile import Tile
from ratroyale.backend.entity import Entity


__all__ = ["VisualManagerEvent"]

# Keep this as a stub until I figure out visual components more concretely.


@dataclass
class VisualManagerEvent(EventToken):
    pass
