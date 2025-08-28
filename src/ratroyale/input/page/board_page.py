from .page import Page
# from backend.board import Board


# TODO: Implement the board page with game elements
class BoardPage(Page):
    def __init__(self, gui_manager, container_rect):
        super().__init__("game", gui_manager, container_rect)