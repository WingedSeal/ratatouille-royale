from __future__ import annotations
from dataclasses import dataclass, field
from typing import Type, Dict
import pygame
from ratroyale.input.constants import ActionKey, PageName, GestureKey
from ratroyale.input.page.wrapped_widgets import WrappedButton, WrappedWidget  # adjust import path

@dataclass
class WidgetConfig:
    type: Type[WrappedWidget]                   # WrappedButton or WrappedWidget class
    rect: pygame.Rect
    button_text: str
    gesture_action_mapping: Dict[GestureKey, ActionKey]
    blocks_input: bool = True
    
@dataclass
class PageConfig:
    name: PageName
    theme_path: str
    blocking: bool
    widgets: list[WidgetConfig] = field(default_factory=list)

# ================================
# region PAGE CONFIGURATIONS
# ================================

MAIN_MENU = PageConfig(
    name=PageName.MAIN_MENU,
    theme_path="",
    blocking=True,
    widgets=[
        WidgetConfig(
            type=WrappedButton,
            rect=pygame.Rect(100, 100, 200, 50),
            button_text="Start",
            gesture_action_mapping={
                GestureKey.CLICK: ActionKey.START_GAME
            }
        ),
        WidgetConfig(
            type=WrappedButton,
            rect=pygame.Rect(100, 200, 200, 50),
            button_text= "Quit",
            gesture_action_mapping={
                GestureKey.CLICK: ActionKey.QUIT
            }
        ),
    ],
)

TEST_SWAP = PageConfig(
    name=PageName.TEST_SWAP,
    theme_path="",
    blocking=True,
    widgets=[
        WidgetConfig(
            type=WrappedButton,
            rect=pygame.Rect(100, 100, 200, 50),
            button_text="Return to Main Menu",
            gesture_action_mapping={
                GestureKey.CLICK: ActionKey.BACK_TO_MENU
            }
        )
    ],
)

BOARD = PageConfig(
    name=PageName.BOARD,
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
    PageName.BOARD: BOARD,
}

