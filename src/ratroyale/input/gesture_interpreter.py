import pygame
import time

class GestureInterpreter:
    CLICK_THRESHOLD = 5
    DRAG_THRESHOLD = 5
    HOLD_THRESHOLD = 0.5
    HOLD_MOVE_TOLERANCE = 10
    DOUBLE_CLICK_TIME = 0.35
    SWIPE_SPEED_THRESHOLD = 800  # pixels per second
    SWIPE_DISTANCE_THRESHOLD = 50  # pixels

    STATE_IDLE = "idle"
    STATE_PRESSED = "pressed"
    STATE_DRAGGING = "dragging"
    STATE_HOLD_TRIGGERED = "hold_triggered"

    def __init__(self):
        self.state = self.STATE_IDLE
        self.start_pos = None
        self.last_pos = None
        self.dragging_last_pos = None
        self.start_time = None
        self.last_click_time = 0
        self.last_click_pos = None

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._on_press(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                self._on_motion(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self._on_release(event.pos)
            elif event.type == pygame.MOUSEWHEEL:
                self._on_scroll(event.x, event.y)
        self._check_hold()

    # --- Internal ---
    def _on_press(self, pos):
        self.state = self.STATE_PRESSED
        self.start_pos = pos
        self.last_pos = pos
        self.start_time = time.time()

    def _on_motion(self, pos):
        if self.state in (self.STATE_PRESSED, self.STATE_HOLD_TRIGGERED, self.STATE_DRAGGING):
            dx = pos[0] - self.start_pos[0]
            dy = pos[1] - self.start_pos[1]
            distance = (dx**2 + dy**2)**0.5

            if distance > self.DRAG_THRESHOLD and self.state != self.STATE_DRAGGING:
                self.state = self.STATE_DRAGGING
                self.dragging_last_pos = self.last_pos
                self._on_drag_start()

            if self.state == self.STATE_DRAGGING:
                dx_frame = pos[0] - self.dragging_last_pos[0]
                dy_frame = pos[1] - self.dragging_last_pos[1]
                self.dragging_last_pos = pos
                self.on_drag(dx_frame, dy_frame)

        self.last_pos = pos

    def _on_release(self, pos):
        if self.start_time is None:
        # Ignore spurious release events
            return

        elapsed_time = time.time() - self.start_time
        dx = pos[0] - self.start_pos[0]
        dy = pos[1] - self.start_pos[1]
        distance = (dx**2 + dy**2)**0.5

        # Swipe detection
        if self.state == self.STATE_DRAGGING and distance >= self.SWIPE_DISTANCE_THRESHOLD:
            speed = distance / max(elapsed_time, 1e-6)
            if speed >= self.SWIPE_SPEED_THRESHOLD:
                self.on_swipe(self.start_pos, pos, dx/distance, dy/distance)

        # Click / double-click
        if self.state == self.STATE_PRESSED:
            current_time = time.time()
            if (
                self.last_click_time > 0
                and current_time - self.last_click_time <= self.DOUBLE_CLICK_TIME
                and self.last_click_pos
                and ((pos[0]-self.last_click_pos[0])**2 + (pos[1]-self.last_click_pos[1])**2)**0.5 <= self.CLICK_THRESHOLD
            ):
                self.on_double_click(pos)
                self.last_click_time = 0
                self.last_click_pos = None
            else:
                self.on_click(pos)
                self.last_click_time = current_time
                self.last_click_pos = pos
        elif self.state == self.STATE_DRAGGING:
            self.on_drag_end()
        elif self.state == self.STATE_HOLD_TRIGGERED:
            pass

        self._reset_state()

    def _check_hold(self):
        if self.state == self.STATE_PRESSED:
            elapsed = time.time() - self.start_time
            dx = self.last_pos[0] - self.start_pos[0]
            dy = self.last_pos[1] - self.start_pos[1]
            distance = (dx**2 + dy**2)**0.5
            if elapsed >= self.HOLD_THRESHOLD and distance <= self.HOLD_MOVE_TOLERANCE:
                self.state = self.STATE_HOLD_TRIGGERED
                self.on_hold(self.start_pos)

    def _on_drag_start(self):
        pass

    def _reset_state(self):
        self.state = self.STATE_IDLE
        self.start_pos = None
        self.last_pos = None
        self.dragging_last_pos = None
        self.start_time = None

    def _on_scroll(self, dx, dy):
        if dy != 0:
            self.on_scroll(dy)


    # --- Callbacks ---
    def on_click(self, pos):
        print("Click at", pos)

    def on_double_click(self, pos):
        print("Double-click at", pos)

    def on_drag(self, dx, dy):
        print("Dragging", dx, dy)

    def on_drag_end(self):
        print("Drag ended")

    def on_hold(self, pos):
        print("Hold triggered at", pos)

    def on_swipe(self, start_pos, end_pos, dir_x, dir_y):
        print(f"Swipe from {start_pos} to {end_pos}, direction ({dir_x:.2f}, {dir_y:.2f})")

    def on_scroll(self, amount):
        print("Scroll:", amount)
