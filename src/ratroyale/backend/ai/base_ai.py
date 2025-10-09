from abc import ABC, abstractmethod
from itertools import chain, combinations

from .ai_action import AIAction, ActivateSkill, EndTurn, MoveAlly, SelectTargets
from ..entity import SkillTargeting
from ..entities.rodent import Rodent
from ..error import NotAITurnError
from ..game_manager import GameManager
from ..side import Side


class BaseAI(ABC):
    def __init__(self, game_manager: GameManager, ai_side: Side) -> None:
        self.game_manager = game_manager
        self.ai_side = ai_side

    def is_ai_turn(self) -> bool:
        return self.game_manager.turn == self.ai_side

    def validate_ai_turn(self) -> None:
        if not self.is_ai_turn():
            raise NotAITurnError()

    @abstractmethod
    def select_action(self, actions: list[AIAction]) -> AIAction:
        """
        The evaluation function to select the action AI will take from all available actions
        """
        ...

    def _get_all_actions(self) -> list[AIAction]:
        skill_targeting = self.game_manager.skill_targeting
        if skill_targeting is not None:
            return self.__get_selecting_target_actions(skill_targeting)
        return self.__get_non_selecting_target_actions()

    def __get_selecting_target_actions(
        self, skill_targeting: SkillTargeting
    ) -> list[AIAction]:
        all_actions: list[AIAction] = []
        # SelectTarget
        for targets in combinations(
            skill_targeting.available_targets, skill_targeting.target_count
        ):
            all_actions.append(SelectTargets(skill_targeting, targets))
        return all_actions

    def __get_non_selecting_target_actions(self) -> list[AIAction]:
        all_actions: list[AIAction] = [EndTurn()]
        cache = self.game_manager.board.cache
        # MoveAlly
        for ally in cache.sides[self.ai_side]:
            if not isinstance(ally, Rodent):
                continue
            if ally.move_stamina <= 0:
                continue
            if self.game_manager.crumbs < ally.move_cost:
                continue
            for move_target_coord in self.game_manager.board.get_reachable_coords(ally):
                all_actions.append(MoveAlly(ally.move_cost, ally, move_target_coord))
        # ActivateSkill
        for entity in chain(cache.sides[self.ai_side], cache.sides[None]):
            if entity.skill_stamina is not None and entity.skill_stamina <= 0:
                continue
            for i, skill in enumerate(entity.skills):
                if self.game_manager.crumbs < skill.crumb_cost:
                    continue
                all_actions.append(ActivateSkill(skill.crumb_cost, entity, i))
        return all_actions
