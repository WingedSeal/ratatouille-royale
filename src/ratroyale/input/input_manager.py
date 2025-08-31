import pygame
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens import PageEvent
from ratroyale.input.constants import ActionKey, PageName, PageEventAction
from dataclasses import dataclass
from typing import Callable
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
            token = self.coordination_manager.input_domain_mailbox.get()
            page_name = token.page_name
            command = token.action_key

            page_registry = self.callback_registry.get(page_name)
            callback = page_registry.get(command) if page_registry is not None else None
            if callback:
                callback()

    # region LEGACY CODE MAY BE PORTED TO PAGE MANAGER
            
    # def gui_process_event_and_consume(self, event):
    #     consumed_by_gui = self.gui_manager.process_events(event)

    #     # Only consume if it's a widget that should block input
    #     # TODO: Separate the widgets list into a file.
    #     if consumed_by_gui:
    #         if hasattr(event, 'ui_element'):
    #             if isinstance(event.ui_element, (UIButton, UITextEntryLine, UISelectionList)):
    #                 return True
    #         return False

    #     # Also consume GUI-specific events
    #     if event.type in CONSUMED_UI_EVENTS:
    #         return True

    #     return False
    
    # def hovering_ui(self, event: pygame.event.Event):
    #     if event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
    #         self.is_hovering_ui = True
    #     elif event.type == pygame_gui.UI_BUTTON_ON_UNHOVERED:
    #         self.is_hovering_ui = False

    # endregion
    