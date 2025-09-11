import pygame
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.base import EventToken
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.input_token import *
from ratroyale.input.input_bindings import create_callback_registry


class InputManager:
    def __init__(self, coordination_manager: CoordinationManager):
        # Callback queue & registry for navigation
        self.coordination_manager = coordination_manager
        self.callback_registry = create_callback_registry(self) # stored in input_bindings.py

    def message(self, event_token: EventToken):
        self.coordination_manager.put_message(event_token)

    def exit(self):
        pygame.quit()
        exit()

    def execute_callbacks(self):
        input_queue = self.coordination_manager.mailboxes[InputManagerEvent]

        while not input_queue.empty():
            token: InputManagerEvent = input_queue.get()

            callback = self.callback_registry.get(token.action_key)
            if callback:
                callback(token)
    