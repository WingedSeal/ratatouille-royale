from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.base import EventToken
from ratroyale.input.dispatch_management.action_name import ActionName
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.input_token import *
from ratroyale.event_tokens.visual_token import *
from ratroyale.input.interactables_management.interactable import TileInteractable, EntityInteractable
from typing import Callable
from ratroyale.input.interactables_management.interaction_type import InteractionType

class InputManager:
    def __init__(self, coordination_manager: CoordinationManager) -> None:
        self.coordination_manager = coordination_manager
        
        self.callback_registry: dict[ActionName, Callable[[InputManagerEvent], None]] = {
            ActionName.START_GAME: lambda tkn: self._message(RequestStart_GameManagerEvent(tkn.page_name)),
            ActionName.QUIT: lambda tkn: self.exit(),
            ActionName.PAUSE_GAME: lambda tkn: self._message(PauseGame_PageManagerEvent(tkn.page_name)),
            ActionName.RESUME_GAME: lambda tkn: self._message(ResumeGame_PageManagerEvent(tkn.page_name)),
            ActionName.BACK_TO_MENU: lambda tkn: self._message(EndGame_PageManagerEvent(tkn.page_name)),

            ActionName.SELECT_TILE: lambda tkn: self._on_select_tile(tkn),
            ActionName.SELECT_UNIT: lambda tkn: self._on_select_entity(tkn),
            ActionName.DISPLAY_ABILITY_MENU: lambda tkn: self._on_display_ability_menu(tkn)
        }

    # region Callback Definitions

    def _message(self, event_token: EventToken) -> None:
        self.coordination_manager.put_message(event_token)

    def _on_select_tile(self, tkn: InputManagerEvent) -> None:
        assert isinstance(tkn.interactable, TileInteractable)
        self._message(TileInteraction_VisualManagerEvent(tkn.page_name, InteractionType.SELECT, tkn.interactable.tile))
        self._message(TileInteraction_PageManagerEvent(tkn.page_name, tkn.interactable.tile))

    def _on_select_entity(self, tkn: InputManagerEvent) -> None:
        assert isinstance(tkn.interactable, EntityInteractable)
        self._message(EntityInteraction_VisualManagerEvent(tkn.page_name, InteractionType.SELECT, tkn.interactable.entity))
        self._message(EntityInteraction_PageManagerEvent(tkn.page_name, tkn.interactable.entity))

    def _on_display_ability_menu(self, tkn: InputManagerEvent) -> None:
        assert isinstance(tkn.interactable, EntityInteractable)
        self._message(EntityAbilityDisplay_PageManagerEvent(tkn.page_name, tkn.interactable.entity))

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
    