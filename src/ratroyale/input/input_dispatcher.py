from ratroyale.input.input_manager import InputManager
from ratroyale.event_tokens import GUIEventSource, InputEventToken
import pygame
from ratroyale.coordination_manager import CoordinationManager

# class InputDispatcher:
#   def __init__(self, coordination_manager: CoordinationManager):
#     pass

#   def handle_gesture(self, gesture_token):
#     print(f"Gesture received: {gesture_token}")

# class InputDispatcherRegistry:
#   def __init__(self, gui_manager: InputManager):
#     self.gm = gui_manager

#     self.gesture_dispatcher_registry = {
#       "MAIN_MENU": {
#         GUIEventSource.UI_ELEMENT: {
#           "CMD_START_GAME": self.change_page("TEST_SWAP"),
#           "CMD_BACK_TO_MENU": self.change_page("MAIN_MENU"),
#           "CMD_QUIT_GAME": self.quit()
#         },
#         GUIEventSource.GESTURE: {

#         }
#       }
#     }
#     pass

#   def change_page(self, page_name: str):
#     self.gm.replace_top(page_name)

  # def quit(self):
  #   pygame.quit()
  #   exit()