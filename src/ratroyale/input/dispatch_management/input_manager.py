from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.base import EventToken
from ratroyale.input.dispatch_management.action_name import ActionName
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.input_token import *

class InputManager:
    def __init__(self, coordination_manager: CoordinationManager) -> None:
        self.coordination_manager = coordination_manager
        
        self.callback_registry = {
            ActionName.START_GAME: lambda tkn: self.message(RequestStart_GameManagerEvent()),
            ActionName.QUIT: lambda tkn: self.exit(),

            ActionName.SELECT_TILE: lambda tkn: print("Tile clicked"),
            ActionName.SELECT_UNIT: lambda tkn: print("Unit clicked"),
            ActionName.PAUSE_GAME: lambda tkn: self.message(PauseGame_PageManagerEvent()),
            ActionName.RESUME_GAME: lambda tkn: self.message(ResumeGame_PageManagerEvent()),
            ActionName.BACK_TO_MENU: lambda tkn: self.message(EndGame_PageManagerEvent())
        }

    def message(self, event_token: EventToken) -> None:
        self.coordination_manager.put_message(event_token)

    # TODO: give coordination_manager its own mailbox to standardize messaging pipeline.
    def exit(self) -> None:
        self.coordination_manager.stop_game()

    def execute_callbacks(self) -> None:
        input_queue = self.coordination_manager.mailboxes[InputManagerEvent]

        while not input_queue.empty():
            token: InputManagerEvent = input_queue.get()

            callback = self.callback_registry.get(token.action_key)
            if callback:
                callback(token)
    