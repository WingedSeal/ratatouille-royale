from dataclasses import dataclass, field
from typing import List
import pygame
import pygame_gui
from ratroyale.input.constants import ActionKey, PageName, GestureKey
from ratroyale.input.page.interactable import Hitbox, RectangleHitbox  
from ratroyale.visual.visual_component import VisualComponent, UIVisual

@dataclass
class InteractableConfig:
    hitbox: Hitbox
    gesture_action_mapping: dict[GestureKey, ActionKey]
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
            hitbox=RectangleHitbox(pygame.Rect(100, 100, 200, 50)),
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
            hitbox=RectangleHitbox(pygame.Rect(100, 200, 200, 50)),
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

PAUSE_BUTTON_PAGE = PageConfig(
    name=PageName.PAUSE_BUTTON,
    theme_path="",
    blocking=False,  # non-blocking, game continues in background
    widgets=[
        InteractableConfig(
            hitbox=RectangleHitbox(pygame.Rect(700, 20, 80, 40)),  # top-right corner (adjust as needed)
            gesture_action_mapping={
                GestureKey.CLICK: ActionKey.PAUSE_GAME
            },
            visuals=[UIVisual(
                type=pygame_gui.elements.UIButton,
                relative_rect=pygame.Rect(700, 20, 80, 40),
                kwargs={"text": "Pause"}
            )]
        )
    ]
)

PAUSE_MENU_PAGE = PageConfig(
    name=PageName.PAUSE_MENU,
    theme_path="",
    blocking=True,  # stops input to underlying game
    widgets=[
        InteractableConfig(
            hitbox=RectangleHitbox(pygame.Rect(300, 200, 200, 50)),
            gesture_action_mapping={
                GestureKey.CLICK: ActionKey.RESUME_GAME
            },
            visuals=[UIVisual(
                type=pygame_gui.elements.UIButton,
                relative_rect=pygame.Rect(300, 200, 200, 50),
                kwargs={"text": "Continue"}
            )]
        ),
        InteractableConfig(
            hitbox=RectangleHitbox(pygame.Rect(300, 300, 200, 50)),
            gesture_action_mapping={
                GestureKey.CLICK: ActionKey.BACK_TO_MENU
            },
            visuals=[UIVisual(
                type=pygame_gui.elements.UIButton,
                relative_rect=pygame.Rect(300, 300, 200, 50),
                kwargs={"text": "Quit Game"}
            )]
        )
    ]
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
    PageName.GAME_BOARD: GAME_BOARD,
    PageName.PAUSE_BUTTON: PAUSE_BUTTON_PAGE,
    PageName.PAUSE_MENU: PAUSE_MENU_PAGE
}