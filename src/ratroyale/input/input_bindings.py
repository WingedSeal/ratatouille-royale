from __future__ import annotations 
from typing import TYPE_CHECKING
from ratroyale.input.constants import ActionKey, PageName
from ratroyale.event_tokens import *
if TYPE_CHECKING:
    from ratroyale.input.input_manager import InputManager  

def create_callback_registry(manager: InputManager):
    return {
            ActionKey.START_GAME: lambda tkn: manager.message_to_game(RequestStart_GameManagerEvent()),
            ActionKey.QUIT: lambda tkn: manager.exit(),

            ActionKey.SELECT_TILE: lambda tkn: print("Tile clicked"),
            ActionKey.SELECT_UNIT: lambda tkn: print("Unit clicked"),
            ActionKey.PAUSE_GAME: lambda tkn: manager.message_to_page(AddPageEvent_PageManagerEvent(PageName.PAUSE_MENU)),
            ActionKey.RESUME_GAME: lambda tkn: manager.message_to_page(RemovePageEvent_PageManagerEvent(PageName.PAUSE_MENU)),
            ActionKey.BACK_TO_MENU: lambda tkn: manager.message_to_page(EndGame_PageManagerEvent())
    }
