import pygame
from typing import Callable
from .page_config_options import PageConfigOptions
from .page import Page
from ratroyale.utils import EventQueue

class PageFactory:
    def __init__(self, gui_manager, screen_size, gui_callback_queue: EventQueue[str]):
        self.gui_manager = gui_manager
        self.screen_size = screen_size
        self.gui_callback_queue = gui_callback_queue
        self.page_option_menu: dict[str, PageConfigOptions] = {
            "MAIN_MENU": PageConfigOptions.MAIN_MENU,
            "TEST_SWAP": PageConfigOptions.TEST_SWAP,
            "BOARD": PageConfigOptions.BOARD
        }

    def create_page(self, page_option: str):
        return Page(self.page_option_menu[page_option], self.screen_size, self.gui_callback_queue)