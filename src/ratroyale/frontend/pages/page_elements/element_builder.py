import pygame
import pygame_gui

from pygame_gui import UIManager
from typing import Callable
from enum import Enum, auto
from ratroyale.frontend.visual.asset_management.visual_component import UIVisual, TileVisual
from ratroyale.frontend.pages.page_elements.element import Element, RectangleHitbox, HexHitbox
from dataclasses import dataclass
from typing import TypeVar, Generic

class ElementType(Enum):
    BUTTON = auto()
    TILE = auto()
    ENTITY = auto()
    ABILITY = auto()

_ELEMENT_BUILDERS: dict[ElementType, Callable] = {}

T = TypeVar('T')

@dataclass
class ElementConfig(Generic[T]):
    element_type: ElementType           # What kind of element this is
    id: str                             # Unique identifier for this element
    rect: tuple[int, int, int, int]     # Rectangle for hitbox / UI element
    text: str = ""                      # Optional text field (for buttons, labels, etc.)
    z_order: int = 0                    # Rendering order, higher is on top
    is_interactable: bool = True        # Whether this element can receive input. If off, it is just visual.
    is_blocking: bool = True            # Whether this element blocks input to those below it

    parent_id: str | None = None        # Optional, for hierarchical element
    offset: tuple[int, int] = (0, 0)    # Optional, for hierarchical element

    payload: T | None = None            # Optional, for any extra data (e.g. Tiles, Entities, Abilities, etc.)

def _register_element_creator(type_key: ElementType):
    def decorator(fn: Callable):
        _ELEMENT_BUILDERS[type_key] = fn
        return fn
    return decorator

def create_element(cfg: ElementConfig, manager: UIManager) -> Element:
  return _ELEMENT_BUILDERS[cfg.element_type](cfg, manager)

@_register_element_creator(ElementType.BUTTON)
def create_button(cfg: ElementConfig, manager: UIManager) -> Element:
    visual = UIVisual(
        type=pygame_gui.elements.UIButton,
        relative_rect=pygame.Rect(cfg.rect),
        kwargs={"text": cfg.text}
    )
    visual.create(manager)
    return Element(
        interactable_id=cfg.id,
        hitbox=RectangleHitbox(pygame.Rect(cfg.rect)),
        visuals=[visual],
        z_order=cfg.z_order,
        is_blocking=cfg.is_blocking
    )

# TODO: NOT FINISHED YET.
# @_register_interactable(InteractableType.TILE)
# def build_tile(cfg, manager: UIManager) -> Interactable:
#     visual = TileVisual(cfg.tile)
#     return Interactable(
#         interactable_id=cfg.id,
#         hitbox=HexHitbox(cfg.tile.get_hitbox()),
#         visuals=[visual],
#     )