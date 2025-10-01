from pathlib import Path

from .backend.map import MAP_FILE_EXTENSION, Map
from .backend.player_info.squeak_set import SqueakSet
from .backend.side import Side
from .backend.game_manager import GameManager
from .game_states import GamePlay, GameState, MainMenu
from .backend.player_info.player_info import SAVE_FILE_EXTENSION, PlayerInfo

SAVE_FILE = f"idk_where_this_is.{SAVE_FILE_EXTENSION}"


class Game:
    """
    The entry-point and the controller class
    """

    def __init__(self) -> None:
        self.player_info = PlayerInfo.from_file(Path(SAVE_FILE))
        self.state: GameState = MainMenu()

    def run(self) -> None:
        # self.renderer.init()
        # while self.renderer.is_running:
        #     match self.state:
        #         case MainMenu():
        #             self.main_menu_tick()
        #         case GamePlay(game_manager):
        #             self.game_play_tick(game_manager)
        #     self.renderer.render_frame(self.state)
        # self.renderer.cleanup()
        pass

    def main_menu_tick(self) -> None:
        # event = self.renderer.input_manager.event_queue.get_or_none()
        # match event:
        #     case TEMP_EVENT_DELETE_LATER():
        #         map_path = Path(
        #             f"path/to/randomly_selected_map_file.{MAP_FILE_EXTENSION}")
        #         map = Map.from_file(map_path)
        #         # Generate AI's side info (deck, etc.)
        #         ai_info = PlayerInfo([], [], 0)
        #         self.state = GamePlay(GameManager(
        #             map, (self.player_info, ai_info), Side.RAT))
        pass

    def game_play_tick(self, game_manager: GameManager) -> None:
        pass
