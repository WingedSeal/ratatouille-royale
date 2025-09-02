from __future__ import annotations 
from typing import TYPE_CHECKING
from ratroyale.input.constants import ActionKey, PageName, PageEventAction, GestureKey
from ratroyale.event_tokens import PageEvent
if TYPE_CHECKING:
    from ratroyale.input.input_manager import InputManager  

# callback_registry broken out of input_manager for modularity
# def create_callback_registry(manager: InputManager):
#   return {
#       PageName.MAIN_MENU: {
#       ActionKey.START_GAME: lambda: manager.message_to_page(PageEvent(PageName.TEST_SWAP, PageEventAction.REPLACE_TOP)),
#       ActionKey.QUIT: manager.exit,
#       ActionKey.DRAG: lambda: print("dragging"),
#       ActionKey.DRAG_END: lambda: print("drag ended"),
#     },
#       PageName.TEST_SWAP: {
#       ActionKey.BACK_TO_MENU: lambda: manager.message_to_page(PageEvent(PageName.MAIN_MENU, PageEventAction.REPLACE_TOP)),
#     },
#   }

def create_callback_registry(manager: InputManager):
    return {
        PageName.MAIN_MENU: {
            GestureKey.CLICK: {
                ActionKey.START_GAME: lambda tkn: manager.message_to_page(PageEvent(PageName.TEST_SWAP, PageEventAction.REPLACE_TOP)),
                ActionKey.QUIT: lambda tkn: manager.exit(),
            }
        },
        PageName.TEST_SWAP: {
            GestureKey.CLICK: {
                ActionKey.BACK_TO_MENU: lambda tkn: manager.message_to_page(PageEvent(PageName.MAIN_MENU, PageEventAction.REPLACE_TOP))
            }
        }
    }
