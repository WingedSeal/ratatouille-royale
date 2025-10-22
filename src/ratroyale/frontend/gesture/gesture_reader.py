import time
from enum import Enum, auto

import pygame

from ratroyale.frontend.gesture.gesture_data import GestureData, GestureType

# Don't ask me about the gesture detection logic inside this. It is borderline arcane.

GESTURE_READER_CARES: list[int] = [
    pygame.MOUSEBUTTONDOWN,
    pygame.MOUSEMOTION,
    pygame.MOUSEBUTTONUP,
]


class GestureState(Enum):
    STATE_IDLE = auto()
    STATE_PRESSED = auto()
    STATE_DRAGGING = auto()
    STATE_HOLD_TRIGGERED = auto()


class GestureReader:
    # region Threshold Variables
    MULTICLICK_MOVEMENT_THRESHOLD = 10
    """
    When attempting to detect multi-clicks, check how far the mouse has moved from the previous click.
    If it is farther than this distance, subsequent clicks won't register as multi-clicks.
    Measured in PX using Euclidean distance.
    """
    MULTICLICK_TIME_THRESHOLD = 0.40
    """
    Maximum time between two clicks to register as a multi-click.
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
        self.click_count: int = 0

        self.gesture_queue: list[GestureData] = []

    def read_events(self, events: list[pygame.event.Event]) -> list[GestureData]:
        """
        Convert a list of raw pygame events into a list of GestureData objects, storing raw_event for downstream processing.
        Currently only detects left clicks.
        """
        self.gesture_queue.clear()

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._on_mousedown(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                self._on_mousemotion(event.pos, raw_event=event)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self._on_mouseup(event.pos, raw_event=event)

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
            self._on_mousedown(pygame.mouse.get_pos())

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

    def _on_mousedown(self, pos: tuple[int, int]) -> None:
        """Called when the pointer is pressed down.

        Sets up the initial state for potential click, drag, or hold gestures.
        """
        self.start_pos = pos
        self.last_pos = pos
        self.start_time = time.perf_counter()
        self.state = GestureState.STATE_PRESSED

        # Reset drag tracking
        self.dragging_last_pos = None

    def _on_mousemotion(
        self, pos: tuple[int, int], raw_event: pygame.event.Event
    ) -> None:
        """Handle pointer motion and generate drag gestures if threshold exceeded."""

        # Always emit hover before any other motion logic
        duration = time.perf_counter() - self.start_time if self.start_time else 0.0
        self.on_hover(
            pos=pos,
            duration=duration,
            raw_event=raw_event,
        )

        if self.start_pos is None:
            return

        if self.last_pos is None:
            self.last_pos = pos
            return

        dx_total = pos[0] - self.start_pos[0]
        dy_total = pos[1] - self.start_pos[1]
        distance_total = (dx_total**2 + dy_total**2) ** 0.5

        # Start drag if movement exceeds threshold
        if (
            distance_total > self.DRAG_MOVEMENT_THRESHOLD
            and self.state != GestureState.STATE_DRAGGING
        ):
            self.state = GestureState.STATE_DRAGGING
            self.dragging_last_pos = self.last_pos
            self._on_drag_start(raw_event)

        # Emit drag events
        if self.state == GestureState.STATE_DRAGGING and self.dragging_last_pos:
            dx_frame = pos[0] - self.dragging_last_pos[0]
            dy_frame = pos[1] - self.dragging_last_pos[1]
            self.dragging_last_pos = pos

            self.on_drag(
                dx=dx_frame,
                dy=dy_frame,
                current_pos=pos,
                start_pos=self.start_pos,
                duration=duration,
                raw_event=raw_event,
            )

        self.last_pos = pos

    def _on_mouseup(self, pos: tuple[int, int], raw_event: pygame.event.Event) -> None:
        """Handle pointer release and produce click, drag-end, swipe, or hold gestures."""

        if self.start_time is None or self.start_pos is None:
            return

        elapsed_time = time.perf_counter() - self.start_time
        dx = pos[0] - self.start_pos[0]
        dy = pos[1] - self.start_pos[1]
        distance_total = (dx**2 + dy**2) ** 0.5

        # --- SWIPE detection ---
        if (
            self.state == GestureState.STATE_DRAGGING
            and distance_total >= self.SWIPE_MOVEMENT_THRESHOLD
        ):
            speed = distance_total / max(elapsed_time, 1e-6)
            if speed >= self.SWIPE_SPEED_THRESHOLD:
                # direction = (dx / speed if speed else 0, dy / speed if speed else 0)
                self.on_swipe(
                    start_pos=self.start_pos,
                    end_pos=pos,
                    velo_x=dx,
                    velo_y=dy,
                    duration=elapsed_time,
                    raw_event=raw_event,
                )

        # --- CLICK / N-CLICK detection ---
        if self.state == GestureState.STATE_PRESSED:
            current_time = time.perf_counter()

            # Check if this is within double/triple click thresholds
            if (
                self.last_click_time is not None
                and self.last_click_pos is not None
                and current_time - self.last_click_time
                <= self.MULTICLICK_TIME_THRESHOLD
                and (
                    (pos[0] - self.last_click_pos[0]) ** 2
                    + (pos[1] - self.last_click_pos[1]) ** 2
                )
                ** 0.5
                <= self.MULTICLICK_MOVEMENT_THRESHOLD
            ):
                self.click_count += 1
            else:
                self.click_count = 1

            self.on_click(
                mouse_pos=self.start_pos,
                duration=elapsed_time,
                click_count=self.click_count,
                raw_event=raw_event,
            )

            # Update last click info
            self.last_click_time = current_time
            self.last_click_pos = pos

        # --- DRAG_END detection ---
        elif self.state == GestureState.STATE_DRAGGING:
            self.on_drag_end(
                current_pos=pos,
                start_pos=self.start_pos,
                duration=elapsed_time,
                raw_event=raw_event,
            )

    def _check_hold(self) -> None:
        if (
            self.state == GestureState.STATE_PRESSED
            and self.start_time is not None
            and self.start_pos is not None
            and self.last_pos is not None
        ):
            elapsed = time.perf_counter() - self.start_time
            dx = self.last_pos[0] - self.start_pos[0]
            dy = self.last_pos[1] - self.start_pos[1]
            distance = (dx**2 + dy**2) ** 0.5

            if (
                elapsed >= self.HOLD_TIME_THRESHOLD
                and distance <= self.HOLD_MOVEMENT_THRESHOLD
            ):
                self.state = GestureState.STATE_HOLD_TRIGGERED
                self.on_hold(pos=self.last_pos, duration=elapsed)

    def _on_drag_start(self, raw_event: pygame.event.Event) -> None:
        """Internal transition to DRAGGING state and trigger DRAG_START event."""
        self.state = GestureState.STATE_DRAGGING
        self.dragging_last_pos = self.last_pos

        # Fire the external DRAG_START gesture
        if self.last_pos is not None:
            duration = (
                time.perf_counter() - self.start_time
                if self.start_time is not None
                else 0.0
            )
            self.on_drag_start(
                current_pos=self.last_pos,
                start_pos=self.start_pos,
                duration=duration,
                raw_event=raw_event,
            )

    def _reset_state(self, reset_click_count: bool = False) -> None:
        """Reset internal gesture state.

        Args:
            reset_click_count: Whether to reset click_count (default False).
                Normally False so sequential clicks can accumulate.
        """
        self.state = GestureState.STATE_IDLE
        self.start_pos = None
        self.last_pos = None
        self.start_time = None
        self.dragging_last_pos = None

        if reset_click_count:
            self.click_count = 0

    # endregion

    # region Event Publisher Hooks
    def on_click(
        self,
        raw_event: pygame.event.Event,
        mouse_pos: tuple[int, int],
        duration: float,
        click_count: int = 1,
    ) -> None:
        self.output_gesture(
            GestureData(
                gesture_type=GestureType.CLICK,
                mouse_pos=mouse_pos,
                duration=duration,
                click_count=click_count,
                raw_event=raw_event,
            )
        )

    def on_drag_start(
        self,
        raw_event: pygame.event.Event,
        current_pos: tuple[int, int],
        start_pos: tuple[int, int] | None = None,
        duration: float = 0.0,
    ) -> None:
        """Trigger a DRAG_START gesture event."""
        self.output_gesture(
            GestureData(
                gesture_type=GestureType.DRAG_START,
                mouse_pos=current_pos,
                start_pos=start_pos,
                duration=duration,
                raw_event=raw_event,
            )
        )

    def on_drag(
        self,
        dx: float,
        dy: float,
        current_pos: tuple[int, int],
        start_pos: tuple[int, int],
        duration: float,
        raw_event: pygame.event.Event,
    ) -> None:
        self.output_gesture(
            GestureData(
                gesture_type=GestureType.DRAG,
                mouse_pos=current_pos,
                start_pos=start_pos,
                delta=(dx, dy),
                duration=duration,
                raw_event=raw_event,
            )
        )

    def on_drag_end(
        self,
        current_pos: tuple[int, int],
        start_pos: tuple[int, int],
        duration: float,
        raw_event: pygame.event.Event,
    ) -> None:
        self.output_gesture(
            GestureData(
                gesture_type=GestureType.DRAG_END,
                mouse_pos=current_pos,
                start_pos=start_pos,
                duration=duration,
                raw_event=raw_event,
            )
        )

    def on_hold(
        self,
        pos: tuple[int, int],
        duration: float,
    ) -> None:
        self.output_gesture(
            GestureData(
                gesture_type=GestureType.HOLD,
                mouse_pos=pos,
                start_pos=pos,
                duration=duration,
            )
        )

    def on_swipe(
        self,
        start_pos: tuple[int, int],
        end_pos: tuple[int, int],
        velo_x: float,
        velo_y: float,
        duration: float,
        raw_event: pygame.event.Event,
    ) -> None:
        speed = (velo_x**2 + velo_y**2) ** 0.5
        direction = (velo_x / speed if speed else 0, velo_y / speed if speed else 0)
        self.output_gesture(
            GestureData(
                gesture_type=GestureType.SWIPE,
                mouse_pos=end_pos,
                start_pos=start_pos,
                delta=(end_pos[0] - start_pos[0], end_pos[1] - start_pos[1]),
                direction=direction,
                speed=speed,
                duration=duration,
                raw_event=raw_event,
            )
        )

    def on_hover(
        self,
        pos: tuple[int, int],
        duration: float,
        raw_event: pygame.event.Event,
    ) -> None:
        self.output_gesture(
            GestureData(
                gesture_type=GestureType.HOVER,
                mouse_pos=pos,
                start_pos=pos,
                duration=duration,
                raw_event=raw_event,
            )
        )

    def output_gesture(self, gesture_data: GestureData) -> None:
        self.gesture_queue.append(gesture_data)

    # endregion
