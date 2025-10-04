import pygame
import time
from ratroyale.frontend.gesture.gesture_data import GestureType, GestureData
from enum import Enum, auto


# TODO: fix strange unresponsive click issues.
class GestureState(Enum):
    STATE_IDLE = auto()
    STATE_PRESSED = auto()
    STATE_DRAGGING = auto()
    STATE_HOLD_TRIGGERED = auto()

class GestureReader:
    # region Threshold Variables
    DBCLICK_MOVEMENT_THRESHOLD = 10
    """
    When attempting to detect double clicks, check how far the mouse has moved from the previous click.
    If it is farther than this distance, the second click does not register as a double click.
    Measured in PX using Euclidean distance.
    """
    DBCLICK_TIME_THRESHOLD = 0.40
    """
    Maximum time between two clicks to register as a double click.
    Measured in SECONDS.
    """

    DRAG_MOVEMENT_THRESHOLD = 5
    """
    How far the mouse has to move while held down to begin a drag sequence.
    Measured in PX using Euclidean distance.
    """

    HOLD_TIME_THRESHOLD = 0.5
    """
    How long the mouse has to be held to register a hold.
    Measured in SECONDS.
    """
    HOLD_MOVEMENT_THRESHOLD = 10
    """
    While holding, if the mouse moves beyond this distance, it cancels the hold and initiates a drag instead.
    Measured in PX using Euclidean distance.
    """

    SWIPE_SPEED_THRESHOLD = 800
    """
    The velocity a drag gesture must reach to be considered a swipe instead.
    Measured in PX/SECONDS using Euclidean distance.
    """
    SWIPE_MOVEMENT_THRESHOLD = 50
    """
    The minimum distance for a drag gesture to be eligible for being considered as a swipe.
    Measured in PX using Euclidean distance.
    """
    # endregion

    def __init__(self) -> None:
        self.state: GestureState = GestureState.STATE_IDLE
        self.start_pos: tuple[int, int] | None = None
        self.last_pos: tuple[int, int] | None = None
        self.dragging_last_pos: tuple[int, int] | None = None
        self.start_time: float | None = None
        self.last_click_time: float | None = None
        self.last_click_pos: tuple[int, int] | None = None

        self.gesture_queue: list[GestureData] = []

    def read_events(self, events: list[pygame.event.Event]) -> list[GestureData]:
        """
        Convert a list of raw pygame events into a list of GestureData objects, storing raw_event for downstream processing.
        """
        self.gesture_queue.clear()

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._on_press(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                self._on_motion(event.pos, raw_event=event)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self._on_release(event.pos, raw_event=event)
            elif event.type == pygame.MOUSEWHEEL:
                self._on_scroll(event.x, event.y, raw_event=event)

        self._check_hold()
        self._sync_with_hardware()
        return self.gesture_queue.copy()

    # region Gesture Logic

    def _sync_with_hardware(self) -> None:
        """Correct our state machine if it desyncs from actual mouse button state."""
        mouse_down = pygame.mouse.get_pressed()[0]

        if not mouse_down and self.state in (
            GestureState.STATE_PRESSED,
            GestureState.STATE_DRAGGING,
            GestureState.STATE_HOLD_TRIGGERED,
        ):
            # Button is up but we still think it's down -> force release
            self._reset_state()
        elif mouse_down and self.state == GestureState.STATE_IDLE:
            # Button is down but we think idle -> fake a press
            self._on_press(pygame.mouse.get_pos())

    def _cancel_active_gestures(self) -> None:
        """Cancels any ongoing gestures (drag, hold, swipe) and resets the state."""
        self.state = GestureState.STATE_IDLE
        self.start_pos = None
        self.last_pos = None
        self.dragging_last_pos = None
        self.start_time = None
        # Optionally reset hold-triggered or click tracking
        self.last_click_time = None
        self.last_click_pos = None

    def _on_press(self, pos: tuple[int, int]) -> None:
        self.state = GestureState.STATE_PRESSED
        self.start_pos = pos
        self.last_pos = pos
        self.start_time = time.time()

    def _on_motion(self, pos: tuple[int, int], raw_event: pygame.event.Event) -> None:
        if (
            self.state
            in (
                GestureState.STATE_PRESSED,
                GestureState.STATE_HOLD_TRIGGERED,
                GestureState.STATE_DRAGGING,
            )
            and self.start_pos is not None
            and self.last_pos is not None
        ):
            dx = pos[0] - self.start_pos[0]
            dy = pos[1] - self.start_pos[1]
            distance = (dx**2 + dy**2) ** 0.5

            if (
                distance > self.DRAG_MOVEMENT_THRESHOLD
                and self.state != GestureState.STATE_DRAGGING
            ):
                self.state = GestureState.STATE_DRAGGING
                self.dragging_last_pos = self.last_pos
                self._on_drag_start()

            if (
                self.state == GestureState.STATE_DRAGGING
                and self.dragging_last_pos is not None
            ):
                dx_frame = pos[0] - self.dragging_last_pos[0]
                dy_frame = pos[1] - self.dragging_last_pos[1]
                self.dragging_last_pos = pos
                self.on_drag(dx_frame, dy_frame, raw_event)

        self.last_pos = pos

    def _on_release(self, pos: tuple[int, int], raw_event: pygame.event.Event) -> None:
        # is_spurious_release_event
        if self.start_time is None or self.start_pos is None:
            return

        elapsed_time = time.time() - self.start_time
        dx = pos[0] - self.start_pos[0]
        dy = pos[1] - self.start_pos[1]
        distance = (dx**2 + dy**2) ** 0.5

        is_swiping = (
            self.state == GestureState.STATE_DRAGGING
            and distance >= self.SWIPE_MOVEMENT_THRESHOLD
        )
        if is_swiping:
            speed = distance / max(elapsed_time, 1e-6)
            if speed >= self.SWIPE_SPEED_THRESHOLD:
                self.on_swipe(
                    self.start_pos, pos, dx / distance, dy / distance, raw_event
                )

        is_clicking = self.state == GestureState.STATE_PRESSED
        if is_clicking:
            current_time = time.time()
            if (
                self.last_click_time is not None
                and self.last_click_pos is not None
                and current_time - self.last_click_time <= self.DBCLICK_TIME_THRESHOLD
                and (
                    (pos[0] - self.last_click_pos[0]) ** 2
                    + (pos[1] - self.last_click_pos[1]) ** 2
                )
                ** 0.5
                <= self.DBCLICK_MOVEMENT_THRESHOLD
            ):
                self.on_double_click(pos, raw_event)
                self.last_click_time = None
                self.last_click_pos = None
            else:
                self.on_click(pos, raw_event)
                self.last_click_time = current_time
                self.last_click_pos = pos
        elif self.state == GestureState.STATE_DRAGGING:
            self.on_drag_end(raw_event)
        elif self.state == GestureState.STATE_HOLD_TRIGGERED:
            pass

        self._reset_state()

    def _check_hold(self) -> None:
        if (
            self.state == GestureState.STATE_PRESSED
            and self.start_time is not None
            and self.start_pos is not None
            and self.last_pos is not None
        ):
            elapsed = time.time() - self.start_time
            dx = self.last_pos[0] - self.start_pos[0]
            dy = self.last_pos[1] - self.start_pos[1]
            distance = (dx**2 + dy**2) ** 0.5
            if (
                elapsed >= self.HOLD_TIME_THRESHOLD
                and distance <= self.HOLD_MOVEMENT_THRESHOLD
            ):
                self.state = GestureState.STATE_HOLD_TRIGGERED
                self.on_hold(self.start_pos)

    def _on_scroll(self, dx: int, dy: int, raw_event: pygame.event.Event) -> None:
        if dy != 0:
            self.on_scroll(dy, raw_event)

    def _on_drag_start(self) -> None:
        pass

    def _reset_state(self) -> None:
        self.state = GestureState.STATE_IDLE
        self.start_pos = None
        self.last_pos = None
        self.dragging_last_pos = None
        self.start_time = None

    # endregion

    # region Callbacks
    def on_click(self, pos: tuple[int, int], raw_event: pygame.event.Event | None = None) -> None:
        self.output_gesture(GestureData(
            gesture_type=GestureType.CLICK, 
            start_pos=pos,
            raw_event=raw_event
        ))

    def on_double_click(self, pos: tuple[int, int], raw_event: pygame.event.Event | None = None) -> None:
        self.output_gesture(GestureData(
            gesture_type=GestureType.DOUBLE_CLICK, 
            start_pos=pos,
            raw_event=raw_event
        ))

    def on_drag(self, dx: int, dy: int, raw_event: pygame.event.Event | None = None) -> None:
        self.output_gesture(GestureData(
            gesture_type=GestureType.DRAG, 
            delta=(dx, dy),
            raw_event=raw_event
        ))

    def on_drag_end(self, raw_event: pygame.event.Event | None = None) -> None:
        self.output_gesture(GestureData(
            gesture_type=GestureType.DRAG_END,
            raw_event=raw_event
        ))

    def on_hold(self, pos: tuple[int, int], raw_event: pygame.event.Event | None = None) -> None:
        self.output_gesture(GestureData(
            gesture_type=GestureType.HOLD, 
            start_pos=pos,
            raw_event=raw_event
        ))

    def on_swipe(
        self,
        start_pos: tuple[int, int],
        end_pos: tuple[int, int],
        velo_x: float,
        velo_y: float,
        raw_event: pygame.event.Event | None = None,
    ) -> None:
        self.output_gesture(GestureData(
            gesture_type=GestureType.SWIPE, 
            start_pos=start_pos, 
            end_pos=end_pos, 
            velocity=(velo_x, velo_y),
            raw_event=raw_event
        ))

    def on_scroll(self, amount: int, raw_event: pygame.event.Event | None = None) -> None:
        self.output_gesture(GestureData(
            gesture_type=GestureType.SCROLL, 
            scroll_amount=amount,
            raw_event=raw_event
        ))

    def output_gesture(self, gesture_data: GestureData) -> None:
        self.gesture_queue.append(gesture_data)

    # endregion
