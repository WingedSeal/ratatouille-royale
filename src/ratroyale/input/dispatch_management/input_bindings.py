from typing import TYPE_CHECKING
from ratroyale.input.dispatch_management.action_name import ActionName
from ratroyale.input.page_management.page_name import PageName # Should be removed later to decouple input dispatching from page management.

from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.input_token import *
from ratroyale.event_tokens.page_token import *

from typing import Callable

if TYPE_CHECKING:
    from ratroyale.input.dispatch_management.input_manager import InputManager  

def create_callback_registry(manager: "InputManager") -> dict[ActionName, Callable[[InputManagerEvent], None]]:
    return {
            ActionName.START_GAME: lambda tkn: manager.message(RequestStart_GameManagerEvent()),
            ActionName.QUIT: lambda tkn: manager.exit(),

            ActionName.SELECT_TILE: lambda tkn: print("Tile clicked"),
            ActionName.SELECT_UNIT: lambda tkn: print("Unit clicked"),
            ActionName.PAUSE_GAME: lambda tkn: manager.message(AddPageEvent_PageManagerEvent(PageName.PAUSE_MENU)),
            ActionName.RESUME_GAME: lambda tkn: manager.message(RemovePageEvent_PageManagerEvent(PageName.PAUSE_MENU)),
            ActionName.BACK_TO_MENU: lambda tkn: manager.message(EndGame_PageManagerEvent())
    }
