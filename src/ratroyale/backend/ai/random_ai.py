from .ai_action import AIAction, EndTurn
from .base_ai import BaseAI
from random import choice


class RandomAI(BaseAI):
    """
    It choose actions randomly except EndTurn. It only EndTurn when there's no other option.
    """

    def get_name_and_description(self) -> tuple[str, str]:
        return "Random-AI", "Exactly as the name said."

    def select_action(self, actions: list[AIAction]) -> AIAction:
        try:
            actions.remove(EndTurn())
        except ValueError:
            pass
        if len(actions) == 0:
            return EndTurn()
        return choice(actions)
