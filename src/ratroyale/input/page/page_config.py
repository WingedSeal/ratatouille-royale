from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
import pygame
import pygame_gui
from ratroyale.input.constants import ActionKey, PageName, GestureKey
from ratroyale.input.page.interactable import Hitbox, RectHitbox  # adjust import path
from ratroyale.visual.visual_component import VisualComponent, UIVisual

@dataclass
class InteractableConfig:
    hitbox: Hitbox
    gesture_action_mapping: Dict[GestureKey, ActionKey]
    blocks_input: bool = True
    visuals: List[VisualComponent] | None = None
    z_order: int = 0
    
@dataclass
class PageConfig:
    name: PageName
    theme_path: str
    blocking: bool
    widgets: list[InteractableConfig] = field(default_factory=list)

# ================================
# region PAGE CONFIGURATIONS
# ================================

MAIN_MENU = PageConfig(
    name=PageName.MAIN_MENU,
    theme_path="",
    blocking=True,
    widgets=[
        InteractableConfig(
            hitbox=RectHitbox(pygame.Rect(100, 100, 200, 50)),
            gesture_action_mapping={
                GestureKey.CLICK: ActionKey.START_GAME
            },
            visuals=[UIVisual(
                type=pygame_gui.elements.UIButton,
                relative_rect=pygame.Rect(100, 100, 200, 50),
                kwargs={"text": "Start"}
            )]
        ),
        InteractableConfig(
            hitbox=RectHitbox(pygame.Rect(100, 200, 200, 50)),
            gesture_action_mapping={
                GestureKey.CLICK: ActionKey.QUIT
            },
            visuals=[UIVisual(
                type=pygame_gui.elements.UIButton,
                relative_rect=pygame.Rect(100, 200, 200, 50),
                kwargs={"text": "Quit"}
            )]
        ),
    ],
)

TEST_SWAP = PageConfig(
    name=PageName.TEST_SWAP,
    theme_path="",
    blocking=True,
    widgets=[
        InteractableConfig(
            hitbox=RectHitbox(pygame.Rect(100, 100, 200, 50)),
            gesture_action_mapping={
                GestureKey.CLICK: ActionKey.BACK_TO_MENU
            },
            visuals=[UIVisual(
                type=pygame_gui.elements.UIButton,
                relative_rect=pygame.Rect(100, 100, 200, 50),
                kwargs={"text": "Return to Main Menu"}
            )]
        )
    ],
)


GAME_BOARD = PageConfig(
    name=PageName.GAME_BOARD,
    theme_path="",
    blocking=True,
    widgets=[],  # no wrapped widgets for board yet
)

# ================================
# region PAGE NAME -> CONFIG REGISTRY
# ================================

PAGES: dict[PageName, PageConfig] = {
    PageName.MAIN_MENU: MAIN_MENU,
    PageName.TEST_SWAP: TEST_SWAP,
    PageName.GAME_BOARD: GAME_BOARD,
}