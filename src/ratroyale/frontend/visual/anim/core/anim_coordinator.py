from ....pages.page_elements.element import ElementWrapper
from .anim_structure import SequentialAnim
from collections import deque
from .....coordination_manager import CoordinationManager
from .....event_tokens.visual_token import VisualManagerEvent


class AnimationCoordinator:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.queue: deque[list[tuple[ElementWrapper, SequentialAnim]]] = deque()
        self._current_anim_set: list[tuple[ElementWrapper, SequentialAnim]] = []
        self._was_running: bool = False  # edge trigger flag

    def queue_animation_set(
        self, anim_set: list[tuple[ElementWrapper, SequentialAnim]]
    ) -> None:
        """Add a new set of animations to run together."""
        self.queue.append(anim_set)

    def queue_to_elements(self) -> None:
        if not self.queue and not self._current_anim_set:
            # detect end-of-queue edge
            if self._was_running:
                self._was_running = False
                self.queue_finished_callback()
            return

        if not self._current_anim_set and self.queue:
            # new animation set begins
            self._current_anim_set = self.queue.popleft()
            for element, seq_anim in self._current_anim_set:
                element.queue_override_animation(seq_anim)
            self._was_running = True

        if self._current_anim_set and self.is_not_running_anim():
            self._current_anim_set.clear()

    def is_not_running_anim(self) -> bool:
        return all(seq_anim.is_finished() for _, seq_anim in self._current_anim_set)

    def queue_finished_callback(self) -> None:
        CoordinationManager.put_message(
            VisualManagerEvent(self.name, "anim_queue_finished")
        )
