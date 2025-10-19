from typing import Callable

import pygame

from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.input_token import InputManagerEvent, post_gesture_event
from ratroyale.event_tokens.page_token import (
    PageCallbackEvent,
    PageManagerEvent,
    PageNavigation,
    PageNavigationEvent,
)
from ratroyale.event_tokens.visual_token import VisualManagerEvent
from ratroyale.frontend.gesture.gesture_reader import (
    GESTURE_READER_CARES,
    GestureReader,
)
from ratroyale.frontend.pages.page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.page_registry import resolve_page
from ratroyale.frontend.pages.page_elements.spatial_component import Camera
from ratroyale.frontend.visual.screen_constants import SCREEN_SIZE_HALVED


class PageManager:
    def __init__(
        self, screen: pygame.surface.Surface, coordination_manager: CoordinationManager
    ) -> None:
        self.screen = screen
        self.coordination_manager = coordination_manager

        self.gesture_reader = GestureReader()
        """Highest level gesture reader. Outputs a gesture to be distributed by the pipeline."""

        self.page_stack: list[Page] = []
        """Active page stack.
        First is bottom-most, while last is topmost"""

        self.camera: Camera = Camera(
            0, 0, SCREEN_SIZE_HALVED[0], SCREEN_SIZE_HALVED[1], 1
        )

        self.page_actions: dict[PageNavigation, Callable[[type[Page]], None]] = {
            PageNavigation.OPEN: self.open_page,
            PageNavigation.CLOSE: self.remove_page,
            PageNavigation.REPLACE_TOP: self.replace_top_page,
        }
        self.global_actions: dict[PageNavigation, Callable[[], None]] = {
            PageNavigation.CLOSE_ALL: self.remove_all_pages,
            PageNavigation.CLOSE_TOP: self.remove_top_page,
        }

    # region Basic Page Management Methods

    def get_page(self, page_type: type[Page]) -> tuple[int, Page]:
        """Return the first page instance of the given type with index."""
        for i, page in enumerate(self.page_stack):
            if isinstance(page, page_type):
                return (i, page)
        raise KeyError(f"{page_type.__name__} is not in stack.")

    def open_page(self, page_type: type[Page]) -> None:
        """Open a page by type or by the given page object on topmost, create if it doesn’t exist yet."""
        try:
            self.get_page(page_type)
        except KeyError:
            opened_page = page_type(self.coordination_manager, self.camera)
            self.page_stack.append(opened_page)
            opened_page.on_open()

    def remove_top_page(self) -> None:
        """Remove the topmost page, or the first page of the given type."""
        if not self.page_stack:
            raise IndexError("Page stack is empty.")
        closed_page = self.page_stack.pop()
        closed_page.on_close()

    def remove_page(self, page_type: type[Page]) -> None:
        for i, page in enumerate(self.page_stack):
            if isinstance(page, page_type):
                closed_page = self.page_stack.pop(i)
                closed_page.on_close()
                break

    def replace_top_page(self, page_to_open: type[Page]) -> None:
        """Switch topmost page for a different one"""
        if self.page_stack:
            self.remove_top_page()
            self.open_page(page_to_open)

    def remove_all_pages(self) -> None:
        """Remove all pages from the stack"""
        while self.page_stack:
            self.remove_top_page()

    def move_up_page(self, page_type: type[Page]) -> None:
        """Finds the given page type, then bring it up one layer"""
        try:
            index = self.get_page(page_type)[0]
        except KeyError as e:
            raise KeyError(f"On BRING_UP: {e}") from e

        if index < len(self.page_stack) - 1:
            self.page_stack[index], self.page_stack[index + 1] = (
                self.page_stack[index + 1],
                self.page_stack[index],
            )

    def move_down_page(self, page_type: type[Page]) -> None:
        """Finds the given page type, then bring it down one layer."""
        try:
            index = self.get_page(page_type)[0]
        except KeyError as e:
            raise KeyError(f"On BRING_DOWN: {e}")

        if index > 0:
            self.page_stack[index - 1], self.page_stack[index] = (
                self.page_stack[index],
                self.page_stack[index - 1],
            )

    def hide_page(self, page_type: type[Page]) -> None:
        self.get_page(page_type)[1].hide()

    def show_page(self, page_type: type[Page]) -> None:
        self.get_page(page_type)[1].show()

    # endregion

    # region Event Handling

    def handle_events(self) -> None:
        """This method propagates gestures downwards through the page stack, until all
        events are consumed, or no pages remain.
        Additionally, this function stops propagating an event if it hits a page
        with a 'blocking' flag set to true."""
        # Step 0: get pygame events
        raw_events = pygame.event.get()

        # Step 1: give raw_events to the gui_manager of each page, topmost to bottommost.
        for page in reversed(self.page_stack):
            for raw_event in raw_events:
                page.gui_manager.process_events(raw_event)

            if page.is_blocking:
                break

        # Step 2: separate mouse events (down, motion, up) from other types.
        mouse_events: list[pygame.event.Event] = []
        other_events: list[pygame.event.Event] = []

        for event in raw_events:
            if event.type in GESTURE_READER_CARES:
                mouse_events.append(event)
            else:
                other_events.append(event)

        # TEMP: gesture creation inspector
        # inspect_gesture_events(other_events)

        # Step 3: produce gesture data
        gestures = self.gesture_reader.read_events(mouse_events)

        # Step 4: distribute gesture data to pages,
        # where pages will distribute gesture data to its elements for posting gesture events.
        for page in reversed(self.page_stack):
            if not gestures:
                break

            gestures = page.handle_gestures(gestures)

            if page.is_blocking:
                break

        # Step 6: for remaining unconsumed gesture, post it into event queue anyways with empty element_id.
        for gesture in gestures:
            post_gesture_event(
                InputManagerEvent[None](element_id=None, gesture_data=gesture)
            )

        # Step 5: other_events gets broadcasted.
        self._broadcast_input(other_events)

    def _broadcast_input(self, events: list[pygame.event.Event]) -> None:
        if not events:
            return

        for event in events:
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
            elif isinstance(msg, PageCallbackEvent):
                self._delegate(msg)

    def _navigate(self, msg: PageNavigationEvent) -> None:
        """Handle page navigation actions such as OPEN, CLOSE, REPLACE, HIDE, SHOW, etc."""
        for action, page_name in msg.action_list:
            page_type = resolve_page(page_name) if page_name else None

            if page_type and action in self.page_actions:
                self.page_actions[action](page_type)
            elif not page_type and action in self.global_actions:
                self.global_actions[action]()
            else:
                raise ValueError(
                    f"Unsupported navigation action {action} for page {page_name}"
                )

    def _delegate(self, msg: PageCallbackEvent) -> None:
        """Delegate a PageCallbackEvent to the appropriate page."""
        print("Callback action:", msg.callback_action)
        for page in self.page_stack:
            page.execute_page_callback(msg)

    # TODO: implement visual events properly
    def execute_visual_callback(self) -> None:
        msg_queue = self.coordination_manager.mailboxes.get(VisualManagerEvent, None)
        if not msg_queue:
            return

        pass

    # endregion

    # region Rendering

    def render(self, delta: float) -> None:
        """Render pages from first to last"""
        for page in self.page_stack:
            if page.is_visible:
                self.screen.blit(page.render(delta), (0, 0))


# endregion
