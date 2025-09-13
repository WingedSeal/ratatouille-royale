from typing import TYPE_CHECKING
from ratroyale.input.constants import ActionKey, PageName

from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.input_token import *
from ratroyale.event_tokens.page_token import *

from typing import Dict, Callable

if TYPE_CHECKING:
    from ratroyale.input.input_manager import InputManager  

def create_callback_registry(manager: InputManager) -> Dict[ActionKey, Callable[[InputManagerEvent], None]]:
    return {
            ActionKey.START_GAME: lambda tkn: manager.message(RequestStart_GameManagerEvent()),
            ActionKey.QUIT: lambda tkn: manager.exit(),

            ActionKey.SELECT_TILE: lambda tkn: print("Tile clicked"),
            ActionKey.SELECT_UNIT: lambda tkn: print("Unit clicked"),
            ActionKey.PAUSE_GAME: lambda tkn: manager.message(AddPageEvent_PageManagerEvent(PageName.PAUSE_MENU)),
            ActionKey.RESUME_GAME: lambda tkn: manager.message(RemovePageEvent_PageManagerEvent(PageName.PAUSE_MENU)),
            ActionKey.BACK_TO_MENU: lambda tkn: manager.message(EndGame_PageManagerEvent())
    }
