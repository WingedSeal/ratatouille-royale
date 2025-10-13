from .ai_action import AIAction
from .base_ai import BaseAI


class RushBAI(BaseAI):
    """
    Place the cheapest rodent in hand in the nearest deployment zone
    at enemy base. The rush straight to it without regard for its life.
    """

    def get_name_and_description(self) -> tuple[str, str]:
        return "RushB", "Your base is not safe."

    def select_action(self, actions: list[AIAction]) -> AIAction:
        raise NotImplementedError()
