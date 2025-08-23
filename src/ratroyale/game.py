from pathlib import Path

from .game_states import MainMenu
from .backend.player_info.player_info import SAVE_FILE_EXTENSION, PlayerInfo
from .render.renderer import Renderer

SAVE_FILE = f"idk_where_this_is.{SAVE_FILE_EXTENSION}"


class Game:
    """
    The entry-point and the controller class 
    """

    def __init__(self) -> None:
        self.renderer = Renderer()
        self.player_info = PlayerInfo.from_file(Path(SAVE_FILE))
        self.state = MainMenu()

    def run(self) -> None:
        self.renderer.init()
        while self.renderer.is_running:
            self.renderer.render_frame(self.state)
        self.renderer.cleanup()
