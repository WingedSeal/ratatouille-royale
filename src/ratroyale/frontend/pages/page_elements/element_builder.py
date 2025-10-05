import pygame
import pygame_gui

from pygame_gui import UIManager
from typing import Callable
from enum import Enum, auto
from ratroyale.frontend.visual.asset_management.visual_component import UIVisual, TileVisual, EntityVisual
from ratroyale.frontend.pages.page_elements.element import Element, RectangleHitbox, HexHitbox
from ratroyale.backend.tile import Tile
from ratroyale.backend.tile import Entity
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
    element_type: ElementType                           # What kind of element this is
    id: str                                             # Unique identifier for this element
    rect: tuple[float, float, float, float]             # Rectangle for hitbox / UI element. If none, override in creation function.
    text: str = ""                                      # Optional text field (for buttons, labels, etc.)
    z_order: int = 0                                    # Rendering order, higher is on top
    is_interactable: bool = True                        # Whether this element can receive input. If off, it is just visual.
    is_blocking: bool = True                            # Whether this element blocks input to those below it

    parent_id: tuple[str, ElementType] | None = None    # Optional, for hierarchical element.
    offset: tuple[int, int] = (0, 0)                    # Offset based on parent's position.

    payload: T | None = None                            # Optional, for any extra data (e.g. Tiles, Entities, Abilities, etc.)

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
        hitbox=RectangleHitbox(cfg.rect),
        visual=visual,
        z_order=cfg.z_order,
        is_blocking=cfg.is_blocking
    )

@_register_element_creator(ElementType.TILE)
def create_tile(cfg: ElementConfig[Tile], manager: UIManager) -> Element:
    if cfg.payload is None:
        raise ValueError("Tile element must have a Tile payload defined.")
    tile = cfg.payload
    visual = TileVisual(tile)
    return Element[Tile](
        interactable_id=cfg.id,
        hitbox=HexHitbox(cfg.rect),
        visual=visual,
        payload=tile
    )

@_register_element_creator(ElementType.ENTITY)
def create_entity(cfg: ElementConfig[Entity], manager: UIManager) -> Element:
    if cfg.payload is None:
        raise ValueError("Entity element must have an Entity payload defined.")
    entity = cfg.payload
    visual = EntityVisual(entity)
    return Element[Entity](
        interactable_id=cfg.id,
        hitbox=HexHitbox(cfg.rect),
        visual=visual,
        z_order=cfg.z_order,
        payload=entity
    )