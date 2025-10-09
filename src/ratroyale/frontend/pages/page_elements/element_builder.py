import pygame_gui
from pygame_gui.core import UIElement

from ratroyale.frontend.visual.asset_management.visual_component import (
    TileVisual,
    EntityVisual,
)
from ratroyale.frontend.pages.page_elements.element import (
    Element,
    HexHitbox,
    RectangleHitbox,
)
from ratroyale.backend.tile import Tile
from ratroyale.backend.entity import Entity
from dataclasses import dataclass
from typing import TypeVar, Generic, ParamSpec, Callable, Any

T = TypeVar("T")
P = ParamSpec("P")
R = TypeVar("R")


@dataclass
class GUITheme:
    """For elements with "pygame_gui" visual component. Allows for CSS-like styling."""

    class_id: str | None = None
    object_id: str | None = None

    def get_object_id(self) -> pygame_gui.core.ObjectID:
        """Return a pygame_gui ObjectID"""
        return pygame_gui.core.ObjectID(
            class_id=f"@{self.class_id}" if self.class_id else None,
            object_id=f"#{self.object_id}" if self.object_id else None,
        )


@dataclass
class ParentIdentity:
    """
    Represents the parent relationship for a UI element.

    Attributes:
        parent_id: The unique identifier of the parent element.
        parent_type: The type of the parent element, defined in the ElementType enum. Optional.
        offset: The offset from the parent's top-left coordinate.
            - If provided, the element snaps to the parent's top-left and applies this offset, ignoring provided rect's position.
            - If None, the offset is automatically calculated from the element's rect relative to the parent's top-left.
    """

    parent_id: str
    parent_type: str | None = None
    offset: tuple[int, int] | None = (0, 0)


@dataclass
class ElementConfig(Generic[T]):
    element_type: str  # What kind of element this is
    id: str  # Unique identifier for this element
    rect: tuple[float, float, float, float]  # Rectangle for hitbox / UI element.
    text: str = ""  # Optional text field (for buttons, labels, etc.)
    z_order: int = 0  # Rendering order, higher is on top
    is_interactable: bool = (
        True  # Whether this element can receive input. If off, it is just visual.
    )
    is_blocking: bool = True  # Whether this element blocks input to those below it

    parent_identity: ParentIdentity | None = None

    gui_theme: GUITheme | None = (
        None  # Optional. For targeting pygame_gui elements with JSON theming.
    )

    payload: T | None = (
        None  # Optional, for any extra data (e.g. Tiles, Entities, Abilities, etc.)
    )


_ELEMENT_BUILDERS: dict[str, Callable[[ElementConfig[Any]], Element[Any]]] = {}


@dataclass
class UIRegisterForm:
    registered_name: str
    ui_element: UIElement


def _register_element_creator(
    type_key: str,
) -> Callable[
    [Callable[[ElementConfig[Any]], "Element[Any]"]],
    Callable[[ElementConfig[Any]], "Element[Any]"],
]:

    def decorator(
        fn: Callable[[ElementConfig[Any]], "Element[Any]"],
    ) -> Callable[[ElementConfig[Any]], "Element[Any]"]:
        _ELEMENT_BUILDERS[type_key] = fn
        return fn

    return decorator


def create_element(cfg: ElementConfig[T]) -> Element[T]:
    return _ELEMENT_BUILDERS[cfg.element_type](cfg)


@_register_element_creator("tile")
def create_tile(cfg: ElementConfig[Tile]) -> Element[Tile]:
    if cfg.payload is None:
        raise ValueError("Tile element must have a Tile payload defined.")
    tile = cfg.payload
    visual = TileVisual(tile)
    return Element[Tile](
        element_id=cfg.id, hitbox=HexHitbox(cfg.rect), visual=visual, payload=tile
    )


@_register_element_creator("entity")
def create_entity(cfg: ElementConfig[Entity]) -> Element[Entity]:
    if cfg.payload is None:
        raise ValueError("Entity element must have an Entity payload defined.")
    entity = cfg.payload
    visual = EntityVisual(entity)
    return Element[Entity](
        element_id=cfg.id,
        hitbox=RectangleHitbox(cfg.rect),
        visual=visual,
        z_order=cfg.z_order,
        payload=entity,
    )
