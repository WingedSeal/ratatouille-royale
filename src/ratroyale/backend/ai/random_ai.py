from .ai_action import AIAction
from .base_ai import BaseAI
from random import choice


class RandomAI(BaseAI):
    def select_action(self, actions: list[AIAction]) -> AIAction:
        return choice(actions)
