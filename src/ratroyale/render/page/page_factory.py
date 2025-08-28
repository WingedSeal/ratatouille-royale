import pygame

from ratroyale.render.page.main_menu_page import MainMenuPage
from ratroyale.render.page.board_page import BoardPage
from ratroyale.render.page.test_swap_page import TestSwapPage

class PageFactory:
    def __init__(self, gui_manager, visual_manager):
        self.gui_manager = gui_manager
        self.visual_manager = visual_manager

    def create_main_menu(self):
        return MainMenuPage(
            self.gui_manager,
            start_callback=lambda: self.visual_manager.set_active_page("return_test"),
            quit_callback=lambda: pygame.quit() or exit()
        )
    
    def create_test_swap_page(self):
        return TestSwapPage(self.gui_manager, return_callback=lambda: self.visual_manager.set_active_page("main_menu"))
    
    # self.visual_manager.switch_page("game")

    def create_board_page(self):
        return BoardPage(self.gui_manager)

    def create_all_pages(self):
        return {
            "main_menu": self.create_main_menu(),
            "game": self.create_board_page(),
            "return_test": self.create_test_swap_page()
        }