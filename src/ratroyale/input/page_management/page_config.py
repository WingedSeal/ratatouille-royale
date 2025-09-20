from dataclasses import dataclass, field
import pygame
import pygame_gui
from ratroyale.input.dispatch_management.action_name import ActionName
from ratroyale.input.gesture_management.gesture_data import GestureType
from ratroyale.input.page_management.page_name import PageName
from ratroyale.input.page_management.interactable import Hitbox, RectangleHitbox  
from ratroyale.visual.asset_management.visual_component import VisualComponent, UIVisual

@dataclass
class InteractableConfig:
    hitbox: Hitbox
    gesture_action_mapping: dict[GestureType, ActionName]
    blocks_input: bool = True
    """
    If this is true, this interactable component stops inputs from reaching any other interactables or pages below it.
    """
    visuals: list[VisualComponent] | None = None
    z_order: int = 0
    
@dataclass
class PageConfig:
    name: PageName
    theme_path: str
    blocking: bool
    """
    If this is true, this page stops inputs from reaching any other interactables or pages below it.
    """
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
                GestureType.CLICK: ActionName.START_GAME
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
                GestureType.CLICK: ActionName.QUIT
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
    blocking=False,  
    widgets=[
        InteractableConfig(
            hitbox=RectangleHitbox(pygame.Rect(700, 20, 80, 40)),  
            gesture_action_mapping={
                GestureType.CLICK: ActionName.PAUSE_GAME
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
    blocking=True,  
    widgets=[
        InteractableConfig(
            hitbox=RectangleHitbox(pygame.Rect(300, 200, 200, 50)),
            gesture_action_mapping={
                GestureType.CLICK: ActionName.RESUME_GAME
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
                GestureType.CLICK: ActionName.BACK_TO_MENU
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
    widgets=[],  
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