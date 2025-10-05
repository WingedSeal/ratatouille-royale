from ratroyale.backend.game_manager import GameManager
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.page_token import *
from typing import Callable
from ratroyale.backend.board import Board
from ratroyale.event_tokens.game_action import GameAction

# TODO: Expand this to handle more backend events as needed. Maybe add decorator-based registration?
class BackendAdapter:
    def __init__(self, game_manager: GameManager, coordination_manager: CoordinationManager) -> None:
        self.game_manager = game_manager
        self.coordination_manager = coordination_manager
        self.event_to_action_map: dict[GameAction, Callable] = {
              GameAction.START_GAME: self.handle_game_start
          }
        
    def execute_backend_callback(self) -> None:
        msg_queue = self.coordination_manager.mailboxes.get(GameManagerEvent, None)
        if not msg_queue:
            return 
        
        while not msg_queue.empty():
            msg = msg_queue.get()
            handler = self.event_to_action_map.get(msg.game_action, None)
            if handler:
                handler(msg)
            else:
                print(f"No handler for event type {type(msg)}")

    def handle_game_start(self, event: GameManagerEvent) -> None:
        board = self.game_manager.board
        if board:
            self.coordination_manager.put_message(PageQueryResponseEvent[Board](
                page_list=["GameBoard"],
                game_action=GameAction.START_GAME,
                payload=board
            ))
        else:
            self.coordination_manager.put_message(PageQueryResponseEvent(
                page_list=["GameBoard"],
                game_action=GameAction.START_GAME,
                success=False,
                error_msg="Failed to start game: Board not initialized",
                payload=None
            ))