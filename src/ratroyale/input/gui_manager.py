import pygame
from ratroyale.input import InputManager, PageFactory, GestureReader, CONSUMED_UI_EVENTS, GestureDispatcher, PageConfigOptions
from ratroyale.utils import EventQueue
from .page.page import Page

class GUIManager:
    def __init__(self, screen: pygame.surface.Surface, gui_callback_queue: EventQueue[str]):
        self.screen = screen
        self.is_hovering_ui = False

        # Helping managers
        self.input_manager = InputManager()
        self.gesture_dispatcher = GestureDispatcher()
        self.gesture_interpreter = GestureReader(self.gesture_dispatcher)

        # Dictionary of pages, each page is a list of UI elements
        self.page_factory = PageFactory(self, self.screen.get_size(), gui_callback_queue)

        # Active page stack
        self.page_stack: list[Page] = []

        # Callback queue & registry for navigation
        self.gui_callback_queue = gui_callback_queue
        self.callback_registry = {
            "start_game": lambda gm=self: gm.replace_top("TEST_SWAP"),
            "quit_game": lambda gm: exit(),
            "back_to_menu": lambda gm=self: gm.replace_top("MAIN_MENU"),
        }

    """ Push page by name, create if it doesn’t exist yet """
    def push_page(self, page_option: str) -> Page:
        # Check if the page already exists in stack
        for page in self.page_stack:
            if page.name == page_option:
                self.page_stack.append(page)
                page.show()
                return page

        # Otherwise, create it on demand
        page = self.page_factory.create_page(page_option)
        self.page_stack.append(page)
        page.show()
        return page
    
    """ Remove topmost page """
    def pop_page(self):
        if self.page_stack:
            page = self.page_stack.pop()
            page.hide()

    """ Switch topmost page for a different one """
    def replace_top(self, page_option: str):
        if self.page_stack:
            self.page_stack[-1].hide()
            self.page_stack.pop()
        self.push_page(page_option)

    def get_active_page(self) -> Page | None:
        return self.page_stack[-1] if self.page_stack else None
    
    """ High-level logical flow:
        # Each page has UI elements and a canvas (pygame.surface).
        # This method propagates events downwards through the page stack, until all
        # events are consumed, or no pages remain.
        # When a page tries to consume an event, it lets the UI elements it contains
        # get the event first, then it will let its internal logic see if it wants 
        # to consume an event.
        # Additionally, this function stops propagating an event if it hits a page 
        # with a 'blocking' flag set to true. """
    def handle_events(self):
        events = self.input_manager.update()
        unconsumed_events = events.copy()  # start with all events

        # Propagate the entire queue through the page stack (top-most first)
        for page in reversed(self.page_stack):
            if not unconsumed_events:
                break  # nothing left to propagate

            # Let the page handle all unconsumed events
            unconsumed_events = page.handle_events(unconsumed_events)

            # If this page is blocking, stop propagation
            if page.blocking:
                break

    def execute_callbacks(self):
        while not self.gui_callback_queue.empty():
            token = self.gui_callback_queue.get()
            print(token)
            callback = self.callback_registry.get(token)
            if callback:
                callback(self)

    # region REFACTOR TO RENDERER

    def update(self, dt):
        for page in reversed(self.page_stack):
            page.gui_manager.update(dt)

    def draw(self):
        for page in reversed(self.page_stack):
            page.gui_manager.draw_ui(self.screen)

    # endregion

    # def handle_events(self):
    #     """Process events and forward unconsumed ones to GestureInterpreter"""
    #     events = self.input_manager.update()
    #     unconsumed_events = []

    #     for event in events:
    #         if event.type == pygame.QUIT:
    #             pygame.quit()
    #             exit()

    #         # Determine if event is consumed by pygame_gui
    #         # Only forward events that are not in our CONSUMED_UI_EVENTS set
    #         self.hovering_ui(event) # Update hovering state
    #         event_consumed = self.gui_process_event_and_consume(event)
    #         if event_consumed:
    #           # Call callbacks for buttons
    #           if event.type == pygame_gui.UI_BUTTON_PRESSED:
    #             active_page = self.get_active_page()
    #             if active_page:
    #                 callback = active_page.get_callback(event.ui_element)
    #                 if callback:
    #                     callback()
    #                 else:
    #                     print(f"No callback found for button: {event.ui_element}")

    #         elif not self.is_hovering_ui:
    #           unconsumed_events.append(event)

    #     # Forward remaining events to gestures
    #     if unconsumed_events:
    #         self.gesture_interpreter.handle_events(unconsumed_events)
            
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
    