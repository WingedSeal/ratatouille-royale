from __future__ import annotations
from dataclasses import dataclass, field
from typing import Type, Any, Callable
import pygame
from ratroyale.input.constants import ActionKey, PageName
from ratroyale.input.page.wrapped_widgets import WrappedButton, WrappedWidget  # adjust import path
# import pygame_gui  # only if you need types for rects

@dataclass
class WidgetConfig:
    type: Type[WrappedWidget]                   # WrappedButton or WrappedWidget class
    action_key: ActionKey
    blocks_input: bool = True
    kwargs: dict[str, Any] = field(default_factory=dict)  # rect, render_callback, button_text, draggable, etc.

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
            action_key=ActionKey.START_GAME,
            kwargs={
                "rect": pygame.Rect(100, 100, 200, 50),
                "render_callback": lambda: print("render callback test"),
                "button_text": "Start",
                "draggable": False,
            },
        ),
        WidgetConfig(
            type=WrappedButton,
            action_key=ActionKey.QUIT,
            kwargs={
                "rect": pygame.Rect(100, 200, 200, 50),
                "render_callback": lambda: print("render callback test"),
                "button_text": "Quit",
                "draggable": False,
            },
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
            action_key=ActionKey.BACK_TO_MENU,
            kwargs={
                "rect": pygame.Rect(100, 100, 200, 50),
                "render_callback": lambda: print("render callback test"),
                "button_text": "Return to Main Menu",
                "draggable": False,
            },
        ),
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

