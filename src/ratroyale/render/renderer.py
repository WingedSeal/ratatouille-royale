from ..game_states import GamePlay, GameState, MainMenu


class Renderer:
    is_running: bool

    def init(self):
        pass

    def render_frame(self, state: GameState):
        match state:
            case MainMenu():
                pass
            case GamePlay(game_manager):
                print(game_manager)

    def cleanup(self):
        pass
