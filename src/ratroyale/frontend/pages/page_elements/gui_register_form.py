from __future__ import annotations
from dataclasses import dataclass
import pygame_gui
from pygame_gui.core import UIElement
from pygame_gui.core import ObjectID
from pygame_gui.ui_manager import UIManager


@dataclass
class GUIRegisterForm:
    registered_name: str
    ui_element: UIElement
