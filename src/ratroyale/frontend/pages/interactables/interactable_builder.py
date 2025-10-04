import pygame
import pygame_gui

from pygame_gui import UIManager
from typing import Callable
from enum import Enum, auto
from ratroyale.frontend.visual.asset_management.visual_component import UIVisual, TileVisual
from ratroyale.frontend.pages.interactables.interactable import Interactable, RectangleHitbox, HexHitbox
from dataclasses import dataclass

class InteractableType(Enum):
    BUTTON = auto()
    TILE = auto()
    ENTITY = auto()
    ABILITY = auto()

_INTERACTABLE_BUILDERS: dict[InteractableType, Callable] = {}

@dataclass
class InteractableConfig:
    type_key: InteractableType          # What kind of interactable this is
    id: str                             # Unique identifier for this interactable
    rect: tuple[int, int, int, int]     # Rectangle for hitbox / UI element
    text: str = ""                      # Optional, for buttons
    z_order: int = 0                    # Rendering order, higher is on top
    is_blocking: bool = True            # Whether this interactable blocks input to those below it

    parent_id: str | None = None        # Optional, for hierarchical interactable
    offset: tuple[int, int] = (0, 0)    # Optional, for hierarchical interactable
    # tile: Tile | None = None          # Optional, for tile visuals
    # entity: Entity | None = None      # Optional, for entity visuals

def _register_interactable(type_key: InteractableType):
    def decorator(fn: Callable):
        _INTERACTABLE_BUILDERS[type_key] = fn
        return fn
    return decorator

def create_interactable(cfg: InteractableConfig, manager: UIManager) -> Interactable:
  return _INTERACTABLE_BUILDERS[cfg.type_key](cfg, manager)

@_register_interactable(InteractableType.BUTTON)
def create_button(cfg: InteractableConfig, manager: UIManager) -> Interactable:
    visual = UIVisual(
        type=pygame_gui.elements.UIButton,
        relative_rect=pygame.Rect(cfg.rect),
        kwargs={"text": cfg.text}
    )
    visual.create(manager)
    return Interactable(
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