import pygame
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens import PageEvent, InputEvent
from ratroyale.input.input_bindings import create_callback_registry


class InputManager:
    def __init__(self, coordination_manager: CoordinationManager):
        # Callback queue & registry for navigation
        self.coordination_manager = coordination_manager
        self.callback_registry = create_callback_registry(self) # stored in input_bindings.py

    def message_to_page(self, page_event_token: PageEvent):
        self.coordination_manager.page_domain_mailbox.put(page_event_token)

    def exit(self):
        pygame.quit()
        exit()

    def execute_callbacks(self):
        while not self.coordination_manager.input_domain_mailbox.empty():
            token: InputEvent = self.coordination_manager.input_domain_mailbox.get()

            page_registry = self.callback_registry.get(token.page_name)
            if not page_registry:
                continue  # no registry for this page

            gesture_registry = page_registry.get(token.gesture_data.gesture_key)
            if not gesture_registry:
                continue  # no callbacks for this gesture on this page

            callback = gesture_registry.get(token.action_key)
            if callback:
                callback(token)  # pass the full InputEvent
    