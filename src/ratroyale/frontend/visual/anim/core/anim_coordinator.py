from ....pages.page_elements.element import ElementWrapper
from .anim_structure import SequentialAnim
from collections import deque


class AnimationCoordinator:
    def __init__(self) -> None:
        self.queue: deque[list[tuple[ElementWrapper, SequentialAnim]]] = deque()
        self._current_anim_set: list[tuple[ElementWrapper, SequentialAnim]] = []

    def queue_animation_set(
        self, anim_set: list[tuple[ElementWrapper, SequentialAnim]]
    ) -> None:
        """Add a new set of animations to run together."""
        self.queue.append(anim_set)

    def queue_to_elements(self) -> None:
        if not self.queue:
            return

        if not self._current_anim_set:
            # Save the animations for keeping track of finished status.
            self._current_anim_set = self.queue.popleft()

            # Delegate all animations to the element.
            for element, seq_anim in self._current_anim_set:
                element.queue_override_animation(seq_anim)

        # Remove the set from current if all animation is finished.
        if self.is_not_running_anim():
            self._current_anim_set.clear()

    def is_not_running_anim(self) -> bool:
        return all(seq_anim.is_finished() for _, seq_anim in self._current_anim_set)
