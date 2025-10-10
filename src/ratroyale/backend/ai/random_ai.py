from .ai_action import AIAction, EndTurn
from .base_ai import BaseAI
from random import choice


class RandomAI(BaseAI):
    def select_action(self, actions: list[AIAction]) -> AIAction:
        actions.remove(EndTurn())
        if len(actions) == 0:
            return EndTurn()
        return choice(actions)
