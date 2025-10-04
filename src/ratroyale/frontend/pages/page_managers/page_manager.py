import pygame
import pygame_gui
from ratroyale.frontend.pages.page_managers.base_page import Page
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.frontend.gesture_management.gesture_reader import GestureReader
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.input_token import InputManagerEvent
from ratroyale.frontend.pages.page_managers.page_registry import resolve_page

class PageManager:
    def __init__(
        self, screen: pygame.surface.Surface, coordination_manager: CoordinationManager
    ) -> None:
        self.screen = screen
        self.coordination_manager = coordination_manager

        self.gesture_reader = GestureReader()
        """Highest level gesture reader. Outputs a gesture to be decorated by the pipeline."""

        self.page_stack: list[Page] = []
        """Active page stack"""


    # region Basic Page Management Methods

    def push_page(self, page_type: type[Page], page: Page | None = None) -> None:
        """Push a page by type or by the given page object, create if it doesn’t exist yet."""
        # Prevent duplicates: only one page of a given type allowed
        if self.get_page(page_type) is not None:
            return

        new_page = page if page else page_type(self.coordination_manager)
        self.page_stack.append(new_page)
        new_page.on_create()

    def pop_page(self) -> None:
        """Remove the topmost page, or the first page of the given type."""
        if not self.page_stack:
            return
        removed = self.page_stack.pop()
        removed.on_destroy()

    def remove_page(self, page_type: type[Page]) -> None:
        for i, page in enumerate(self.page_stack):
                if isinstance(page, page_type):
                    removed = self.page_stack.pop(i)
                    removed.on_destroy()
                    break

    def get_page(self, page_type: type[Page]) -> Page | None:
        """Return the first page instance of the given type."""
        for page in self.page_stack:
            if isinstance(page, page_type):
                return page
        return None

    def replace_top(self, page_type: type[Page], page: Page | None) -> None:
        """ Switch topmost page for a different one """
        if self.page_stack:
            self.pop_page()
            self.push_page(page_type, page)

    def remove_all_pages(self) -> None:
        """ Remove all pages from the stack """
        while self.page_stack:
            self.pop_page()

    # endregion

    # region Event Handling

    def handle_events(self) -> None:
        """This method propagates gestures downwards through the page stack, until all
        events are consumed, or no pages remain.
        Additionally, this function stops propagating an event if it hits a page
        with a 'blocking' flag set to true."""
        raw_events = pygame.event.get()
        gestures = self.gesture_reader.read_events(raw_events)

        for page in reversed(self.page_stack):
            if not gestures:
                break  

            gestures = page.handle_gestures(gestures)

            if page.is_blocking:
                break

        self._dispatch_input_messages()

    def _dispatch_input_messages(self) -> None:
        """Pull all InputManagerEvents from the coordination manager and send them to pages."""
        msg_queue = self.coordination_manager.mailboxes.get(InputManagerEvent, None)
        if not msg_queue:
            return

        while not msg_queue.empty():
            event: InputManagerEvent = msg_queue.get()
            # Broadcast to all pages that have a handler for this event
            for page in reversed(self.page_stack):
                page.execute_input_callback(event)

    def execute_page_callback(self) -> None:
        msg_queue = self.coordination_manager.mailboxes.get(PageManagerEvent, None)
        if not msg_queue:
            return 
        
        while not msg_queue.empty():
            msg = msg_queue.get()
            if isinstance(msg, PageNavigationEvent):
                self._navigate(msg)
            elif isinstance(msg, PageTargetedEvent):
                self._delegate(msg)
    
    def _navigate(self, msg: PageNavigationEvent) -> None:
        """ Handle page navigation actions such as PUSH, POP, REPLACE, HIDE, and SHOW."""
        print(f"Navigating pages with actions: {msg.action_list}")
        for action, page_name in msg.action_list:
            page_type = resolve_page(page_name) if page_name else None

            if page_type:
                match action:
                    case PageNavigation.PUSH:
                        self.push_page(page_type)
                    case PageNavigation.REMOVE:
                        self.remove_page(page_type)
                    case PageNavigation.REPLACE:
                        self.replace_top(page_type, None)
                    case PageNavigation.HIDE:
                        page = self.get_page(page_type)
                        if page:
                            page.hide()
                    case PageNavigation.SHOW:
                        page = self.get_page(page_type)
                        if page:
                            page.show()
            else:
                match action:
                    case PageNavigation.REMOVE_ALL:
                        self.remove_all_pages()
                    case PageNavigation.POP:
                        self.pop_page()

    def _delegate(self, msg: PageTargetedEvent) -> None:
        """Delegate a PageManagerEvent to the appropriate page."""
        page = self.get_page(resolve_page(msg.page_name))
        if page:
            page.execute_page_callback(msg)    
        else:
            print(f"No page of type {msg.page_name} to handle {msg}")

    def execute_visual_callback(self) -> None:
        msg_queue = self.coordination_manager.mailboxes.get(VisualManagerEvent, None)
        if not msg_queue:
            return 
        
        while not msg_queue.empty():
            msg = msg_queue.get()
            if isinstance(msg, PageNavigationEvent):
                self._navigate(msg)
            elif isinstance(msg, PageTargetedEvent):
                self._delegate(msg)

    # endregion

    # region Rendering
    
    def render(self, delta: float) -> None:
        """Render pages bottom-up."""
        for page in self.page_stack:
            if page.is_visible:
                self.screen.blit(page.render(delta), (0, 0))
