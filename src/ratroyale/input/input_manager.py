import pygame
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.input_token import *
from ratroyale.input.input_bindings import create_callback_registry


class InputManager:
    def __init__(self, coordination_manager: CoordinationManager):
        # Callback queue & registry for navigation
        self.coordination_manager = coordination_manager
        self.callback_registry = create_callback_registry(self) # stored in input_bindings.py

    def message_to_page(self, page_event_token: PageManagerEvent):
        self.coordination_manager.page_domain_mailbox.put(page_event_token)

    def message_to_game(self, game_event_token: GameManagerEvent):
        self.coordination_manager.game_domain_mailbox.put(game_event_token)

    def exit(self):
        pygame.quit()
        exit()

    def execute_callbacks(self):
        while not self.coordination_manager.input_domain_mailbox.empty():
            token: InputManagerEvent = self.coordination_manager.input_domain_mailbox.get()

            callback = self.callback_registry.get(token.action_key)
            if callback:
                callback(token)
    