from random import choice

from .ai_action import AIAction, EndTurn
from .base_ai import BaseAI


class RandomAI(BaseAI):
    def select_action(self, actions: list[AIAction]) -> AIAction:
        try:
            actions.remove(EndTurn())
        except ValueError:
            pass
        if len(actions) == 0:
            return EndTurn()
        return choice(actions)
