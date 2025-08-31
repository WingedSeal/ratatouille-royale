from __future__ import annotations
from dataclasses import dataclass, field
from typing import Type, Any
import pygame
import pygame_gui
from ratroyale.input.constants import ActionKey, PageName

@dataclass
class WidgetConfig:
    type: Type[Any]                  # Widget class, e.g. pygame_gui.elements.UIButton
    action_key: ActionKey
    kwargs: dict[str, Any] = field(default_factory=dict)


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
            type=pygame_gui.elements.UIButton,
            action_key=ActionKey.START_GAME,
            kwargs={"text": "Start", "relative_rect": pygame.Rect(100, 100, 200, 50)},
        ),
        WidgetConfig(
            type=pygame_gui.elements.UIButton,
            action_key=ActionKey.QUIT,
            kwargs={"text": "Quit", "relative_rect": pygame.Rect(100, 200, 200, 50)},
        ),
    ],
)

TEST_SWAP = PageConfig(
    name=PageName.TEST_SWAP,
    theme_path="",
    blocking=True,
    widgets=[
        WidgetConfig(
            type=pygame_gui.elements.UIButton,
            action_key=ActionKey.BACK_TO_MENU,
            kwargs={"text": "Return to Main Menu", "relative_rect": pygame.Rect(100, 100, 200, 50)},
        )
    ],
)

BOARD = PageConfig(
    name=PageName.BOARD,
    theme_path="",
    blocking=True,
    widgets=[],
)

# endregion

# ==================================
# region: PAGE NAME - CONFIG REGISTRY
# ==================================

PAGES: dict[PageName, PageConfig] = {
    PageName.MAIN_MENU: MAIN_MENU,
    PageName.TEST_SWAP: TEST_SWAP,
    PageName.BOARD: BOARD,
}

# endregion
