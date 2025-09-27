from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.base import EventToken
from ratroyale.input.dispatch_management.action_name import ActionName
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.input_token import *
from ratroyale.event_tokens.visual_token import *
from ratroyale.input.page_management.interactable import TileInteractable, EntityInteractable
from typing import Callable

class InputManager:
    def __init__(self, coordination_manager: CoordinationManager) -> None:
        self.coordination_manager = coordination_manager
        
        self.callback_registry: dict[ActionName, Callable[[InputManagerEvent], None]] = {
            ActionName.START_GAME: lambda tkn: self.message(RequestStart_GameManagerEvent()),
            ActionName.QUIT: lambda tkn: self.exit(),

            ActionName.SELECT_TILE: lambda tkn: self.on_select_tile(tkn),
            ActionName.SELECT_UNIT: lambda tkn: self.on_select_entity(tkn),
            ActionName.PAUSE_GAME: lambda tkn: self.message(PauseGame_PageManagerEvent()),
            ActionName.RESUME_GAME: lambda tkn: self.message(ResumeGame_PageManagerEvent()),
            ActionName.BACK_TO_MENU: lambda tkn: self.message(EndGame_PageManagerEvent())
        }

    # region Callback Definitions

    def message(self, event_token: EventToken) -> None:
        self.coordination_manager.put_message(event_token)

    def on_select_tile(self, tkn: InputManagerEvent) -> None:
        assert isinstance(tkn.interactable, TileInteractable)
        self.message(TileInteraction_VisualManagerEvent(InteractionType.SELECT, tkn.interactable.tile))

    def on_select_entity(self, tkn: InputManagerEvent) -> None:
        assert isinstance(tkn.interactable, EntityInteractable)
        self.message(EntityInteraction_VisualManagerEvent(InteractionType.SELECT, tkn.interactable.entity))

    # TODO: give coordination_manager its own mailbox to standardize messaging pipeline.
    def exit(self) -> None:
        self.coordination_manager.stop_game()

    # endregion

    def execute_callbacks(self) -> None:
        input_queue = self.coordination_manager.mailboxes[InputManagerEvent]

        while not input_queue.empty():
            token: InputManagerEvent = input_queue.get()

            callback = self.callback_registry.get(token.action_key)
            if callback:
                callback(token)
    