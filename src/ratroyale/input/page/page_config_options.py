from enum import Enum
import pygame_gui
import pygame
from torch import FutureType

class PageConfigOptions(Enum):
    MAIN_MENU = {
        "name": "MAIN_MENU",
        "theme_path": "", 
        "blocking": True,
        "widgets": [
            {"type": pygame_gui.elements.UIButton, 
             "callback_key": "CMD_START_GAME",
             "kwargs": {
                 "text": "Start", 
                 "relative_rect": pygame.Rect(100,100,200,50)}}, 
            {"type": pygame_gui.elements.UIButton, 
             "callback_key": "CMD_QUIT_GAME",
             "kwargs": {
                 "text": "Quit", 
                 "relative_rect": pygame.Rect(100,200,200,50)}}
            ]
        }
    TEST_SWAP = {
        "name": "TEST_SWAP",
        "theme_path": "", 
        "blocking": True,
        "widgets": [
            {"type": pygame_gui.elements.UIButton, 
             "callback_key": "CMD_BACK_TO_MENU",
             "kwargs": {
                 "text": "Return to Main Menu", 
                 "relative_rect": pygame.Rect(100,100,200,50)}}
            ]
        }
    BOARD = {
        "name": "BOARD",
        "theme_path": "", 
        "blocking": True,
        "widgets": []
        }