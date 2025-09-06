from __future__ import annotations 
from typing import TYPE_CHECKING
from ratroyale.input.constants import ActionKey, PageName, PageEventAction
from ratroyale.event_tokens import PageEvent
if TYPE_CHECKING:
    from ratroyale.input.input_manager import InputManager  

def create_callback_registry(manager: InputManager):
    return {
        PageName.MAIN_MENU: {
            ActionKey.START_GAME: lambda tkn: manager.message_to_page(PageEvent(PageName.GAME_BOARD, PageEventAction.REPLACE_TOP)),
            ActionKey.QUIT: lambda tkn: manager.exit(),
        },
        PageName.TEST_SWAP: {
            ActionKey.BACK_TO_MENU: lambda tkn: manager.message_to_page(PageEvent(PageName.MAIN_MENU, PageEventAction.REPLACE_TOP))
        },
        PageName.GAME_BOARD: {
            ActionKey.SELECT_TILE: lambda tkn: print("Tile clicked"),
            ActionKey.SELECT_UNIT: lambda tkn: print("Unit clicked")
        }
    }
