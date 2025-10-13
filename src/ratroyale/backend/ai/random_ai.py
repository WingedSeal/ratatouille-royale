from .ai_action import AIAction, AIActions, EndTurn
from .base_ai import BaseAI
from random import choice


class RandomAI(BaseAI):
    """
    It choose actions randomly except EndTurn. It only EndTurn when there's no other option.
    """

    def get_name_and_description(self) -> tuple[str, str]:
        return "Random-AI", "Exactly as the name said."

    def select_action(self, actions: AIActions) -> AIAction:
        actions.end_turn = []
        flatten_actions = actions.flattern()
        if len(flatten_actions) == 0:
            return EndTurn()
        return choice(flatten_actions)
