from typing import cast

from ratroyale.backend.player_info.squeak import SqueakType
from ratroyale.backend.tags import SkillTag
from ..entities.rodent import Rodent
from .ai_action import AIAction, PlaceSqueak, SelectTargets
from .base_ai import BaseAI


class RushBAI(BaseAI):
    """
    Place the cheapest rodent in hand in the nearest deployment zone
    at enemy base. The rush straight to it without regard for its life.
    """

    def get_name_and_description(self) -> tuple[str, str]:
        return "RushB", "Your base is not safe."

    def is_ally_on_field(self) -> bool:
        for entity in self.game_manager.board.cache.sides[self.ai_side]:
            if isinstance(entity, Rodent):
                return True
        return False

    def select_hand(self, hands: list[PlaceSqueak]) -> PlaceSqueak | None:
        for hand in sorted(hands, key=lambda action: action.crumb_cost):
            if hand.squeak.squeak_type != SqueakType.RODENT:
                continue
            rodent = hand.squeak.rodent_or_trick
            for skill in rodent.skills:
                if SkillTag.NO_TARGET_FEATURE not in skill.tags:
                    return hand
        return None

    def select_action(self, actions: list[AIAction]) -> AIAction:
        if self.game_manager.is_selecting_target:
            select_targets_actions = cast(list[SelectTargets], actions)
            return select_targets_actions[0]  # TODO: Select Skill

        raise NotImplementedError()

        if not self.is_ally_on_field():
            pass
