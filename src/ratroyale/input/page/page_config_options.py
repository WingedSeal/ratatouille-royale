from enum import Enum
import pygame_gui
from ..gesture_reader import GestureType
import pygame

class PageConfigOptions(Enum):
    MAIN_MENU = {
        "name": "MAIN_MENU",
        "theme_path": "", 
        "blocking": True,
        "widgets": [
            {"type": pygame_gui.elements.UIButton, 
             "callback_key": "start_game",
             "kwargs": {
                 "text": "Start", 
                 "relative_rect": pygame.Rect(100,100,200,50)}}, 
            {"type": pygame_gui.elements.UIButton, 
             "callback_key": "quit_game",
             "kwargs": {
                 "text": "Quit", 
                 "relative_rect": pygame.Rect(100,200,200,50)}}
            ],
        "gesture_mapping": {
            GestureType.DRAG: lambda token: print(token),
            GestureType.DRAG_END: lambda token: print(token)
            }
        }
    TEST_SWAP = {
        "name": "TEST_SWAP",
        "theme_path": "", 
        "blocking": True,
        "widgets": [
            {"type": pygame_gui.elements.UIButton, 
             "callback_key": "back_to_menu",
             "kwargs": {
                 "text": "Return to Main Menu", 
                 "relative_rect": pygame.Rect(100,100,200,50)}}
            ],
        "gesture_mapping": {
            GestureType.DRAG: lambda token: print(token),
            GestureType.DRAG_END: lambda: print("drag ended")
            }
        }
    BOARD = {
        "name": "BOARD",
        "theme_path": "", 
        "blocking": True,
        "widgets": [],
        "gesture_mapping": {
            GestureType.DRAG: lambda token: print(token),
            GestureType.DRAG_END: lambda token: print(token)
            }
        }