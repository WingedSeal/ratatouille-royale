import pygame
import time
from ratroyale.event_tokens.input_token import GestureData
from ratroyale.input.constants import GestureKey
from typing import List, Tuple

# TODO: fix strange unresponsive click issues.
class GestureReader:
    CLICK_THRESHOLD = 10
    DRAG_THRESHOLD = 5
    HOLD_THRESHOLD = 0.5
    HOLD_MOVE_TOLERANCE = 10
    DOUBLE_CLICK_TIME = 0.40
    SWIPE_SPEED_THRESHOLD = 800  # pixels per second
    SWIPE_DISTANCE_THRESHOLD = 50  # pixels

    STATE_IDLE = "idle"
    STATE_PRESSED = "pressed"
    STATE_DRAGGING = "dragging"
    STATE_HOLD_TRIGGERED = "hold_triggered"

    def __init__(self):
        self.state: str = self.STATE_IDLE
        self.start_pos: tuple[int, int] | None = None
        self.last_pos: tuple[int, int] | None = None
        self.dragging_last_pos: tuple[int, int] | None = None
        self.start_time: float | None = None
        self.last_click_time: float | None = None
        self.last_click_pos: tuple[int, int] | None = None

        self.gesture_queue: List[GestureData] = []

    # region Gesture Logic

    def read_events(self, events: list[pygame.event.Event]) -> list[GestureData]:
        """
        Convert raw pygame events into GestureData objects, storing raw_event for downstream processing.
        """
        # Clear old gesture queue
        self.gesture_queue.clear()

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
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


    # --- Internal ---
    def _sync_with_hardware(self):
        """Correct our state machine if it desyncs from actual mouse button state."""
        mouse_down = pygame.mouse.get_pressed()[0]

        if not mouse_down and self.state in (self.STATE_PRESSED, self.STATE_DRAGGING, self.STATE_HOLD_TRIGGERED):
            # Button is up but we still think it's down → force release
            self._reset_state()
        elif mouse_down and self.state == self.STATE_IDLE:
            # Button is down but we think idle → fake a press
            self._on_press(pygame.mouse.get_pos())

    def _cancel_active_gestures(self):
        """Cancels any ongoing gestures (drag, hold, swipe) and resets the state."""
        self.state = self.STATE_IDLE
        self.start_pos = None
        self.last_pos = None
        self.dragging_last_pos = None
        self.start_time = None
        # Optionally reset hold-triggered or click tracking
        self.last_click_time = None
        self.last_click_pos = None

    def _on_press(self, pos: tuple[int, int]) -> None:
        self.state = self.STATE_PRESSED
        self.start_pos = pos
        self.last_pos = pos
        self.start_time = time.time()

    def _on_motion(self, pos: tuple[int, int], raw_event: pygame.event.Event) -> None:
        if (
            self.state in (self.STATE_PRESSED, self.STATE_HOLD_TRIGGERED, self.STATE_DRAGGING)
            and self.start_pos is not None
            and self.last_pos is not None
        ):
            dx = pos[0] - self.start_pos[0]
            dy = pos[1] - self.start_pos[1]
            distance = (dx**2 + dy**2) ** 0.5

            if distance > self.DRAG_THRESHOLD and self.state != self.STATE_DRAGGING:
                self.state = self.STATE_DRAGGING
                self.dragging_last_pos = self.last_pos
                self._on_drag_start()

            if self.state == self.STATE_DRAGGING and self.dragging_last_pos is not None:
                dx_frame = pos[0] - self.dragging_last_pos[0]
                dy_frame = pos[1] - self.dragging_last_pos[1]
                self.dragging_last_pos = pos
                self.on_drag(dx_frame, dy_frame, raw_event)

        self.last_pos = pos

    def _on_release(self, pos: tuple[int, int], raw_event: pygame.event.Event) -> None:
        if self.start_time is None or self.start_pos is None:
            # Ignore spurious release events
            return

        elapsed_time = time.time() - self.start_time
        dx = pos[0] - self.start_pos[0]
        dy = pos[1] - self.start_pos[1]
        distance = (dx**2 + dy**2) ** 0.5

        IS_SWIPING = self.state == self.STATE_DRAGGING and distance >= self.SWIPE_DISTANCE_THRESHOLD
        if IS_SWIPING:
            speed = distance / max(elapsed_time, 1e-6)
            if speed >= self.SWIPE_SPEED_THRESHOLD:
                self.on_swipe(self.start_pos, pos, dx / distance, dy / distance, raw_event)

        IS_CLICKING = self.state == self.STATE_PRESSED
        if IS_CLICKING:
            current_time = time.time()
            if (
                self.last_click_time is not None
                and self.last_click_pos is not None
                and current_time - self.last_click_time <= self.DOUBLE_CLICK_TIME
                and ((pos[0] - self.last_click_pos[0]) ** 2 + (pos[1] - self.last_click_pos[1]) ** 2) ** 0.5
                <= self.CLICK_THRESHOLD
            ):
                self.on_double_click(pos, raw_event)
                self.last_click_time = None
                self.last_click_pos = None
            else:
                self.on_click(pos, raw_event)
                self.last_click_time = current_time
                self.last_click_pos = pos
        elif self.state == self.STATE_DRAGGING:
            self.on_drag_end(raw_event)
        elif self.state == self.STATE_HOLD_TRIGGERED:
            pass

        self._reset_state()

    def _check_hold(self) -> None:
        if self.state == self.STATE_PRESSED and self.start_time is not None and self.start_pos is not None and self.last_pos is not None:
            elapsed = time.time() - self.start_time
            dx = self.last_pos[0] - self.start_pos[0]
            dy = self.last_pos[1] - self.start_pos[1]
            distance = (dx**2 + dy**2) ** 0.5
            if elapsed >= self.HOLD_THRESHOLD and distance <= self.HOLD_MOVE_TOLERANCE:
                self.state = self.STATE_HOLD_TRIGGERED
                self.on_hold(self.start_pos)

    def _on_scroll(self, dx: int, dy: int, raw_event: pygame.event.Event) -> None:
        if dy != 0:
            self.on_scroll(dy, raw_event)

    def _on_drag_start(self) -> None:
        pass

    def _reset_state(self) -> None:
        self.state = self.STATE_IDLE
        self.start_pos = None
        self.last_pos = None
        self.dragging_last_pos = None
        self.start_time = None

    # endregion

    # --- Callbacks ---
    def on_click(self, pos: Tuple[int, int], raw_event: pygame.event.Event | None = None) -> None:
        self.output_gesture(GestureData(
            gesture_key=GestureKey.CLICK, 
            start_pos=pos,
            raw_event=raw_event
        ))

    def on_double_click(self, pos: Tuple[int, int], raw_event: pygame.event.Event | None = None) -> None:
        self.output_gesture(GestureData(
            gesture_key=GestureKey.DOUBLE_CLICK, 
            start_pos=pos,
            raw_event=raw_event
        ))

    def on_drag(self, dx: int, dy: int, raw_event: pygame.event.Event | None = None) -> None:
        self.output_gesture(GestureData(
            gesture_key=GestureKey.DRAG, 
            delta=(dx, dy),
            raw_event=raw_event
        ))

    def on_drag_end(self, raw_event: pygame.event.Event | None = None) -> None:
        self.output_gesture(GestureData(
            gesture_key=GestureKey.DRAG_END,
            raw_event=raw_event
        ))

    def on_hold(self, pos: Tuple[int, int], raw_event: pygame.event.Event | None = None) -> None:
        self.output_gesture(GestureData(
            gesture_key=GestureKey.HOLD, 
            start_pos=pos,
            raw_event=raw_event
        ))

    def on_swipe(
        self, 
        start_pos: Tuple[int, int], 
        end_pos: Tuple[int, int], 
        velo_x: float, 
        velo_y: float, 
        raw_event: pygame.event.Event | None = None
    ) -> None:
        self.output_gesture(GestureData(
            gesture_key=GestureKey.SWIPE, 
            start_pos=start_pos, 
            end_pos=end_pos, 
            velocity=(velo_x, velo_y),
            raw_event=raw_event
        ))

    def on_scroll(self, amount: int, raw_event: pygame.event.Event | None = None) -> None:
        self.output_gesture(GestureData(
            gesture_key=GestureKey.SCROLL, 
            scroll_amount=amount,
            raw_event=raw_event
        ))

    def output_gesture(self, gesture_data: GestureData) -> None:
        self.gesture_queue.append(gesture_data)
