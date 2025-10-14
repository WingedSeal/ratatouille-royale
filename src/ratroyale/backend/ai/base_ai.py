from abc import ABC, abstractmethod
from itertools import chain, combinations


from ..entities.rodent import Rodent
from ..entity import SkillCompleted, SkillTargeting
from ..error import NotAITurnError
from ..game_manager import GameManager
from ..side import Side
from .ai_action import (
    AIActions,
    ActivateSkill,
    AIAction,
    EndTurn,
    MoveAlly,
    PlaceSqueak,
    SelectTargets,
)


class BaseAI(ABC):
    def __init__(self, game_manager: GameManager, ai_side: Side) -> None:
        self.game_manager = game_manager
        self.ai_side = ai_side

    def is_ai_turn(self) -> bool:
        return self.game_manager.turn == self.ai_side

    def validate_ai_turn(self) -> None:
        if not self.is_ai_turn():
            raise NotAITurnError()

    def run_ai_and_update_game_manager(self) -> None:
        self.validate_ai_turn()
        banned_actions: list[ActivateSkill] = []
        is_banned_actions_updated = False
        """Banned AIAction to prevent activing skill that get cancelled over and over"""
        while self.is_ai_turn():
            if self.game_manager.game_over_event is not None:
                return
            if (
                not is_banned_actions_updated
            ):  # If banned action wasn't updated, it means that it did something
                # that updated the game state. Hence the ban should be lifted
                banned_actions = []
            actions = self._get_all_actions()
            for banned_action in banned_actions:
                try:
                    actions.activate_skill.remove(banned_action)
                except ValueError:
                    pass
            action = self.select_action(actions)
            is_banned_actions_updated = False
            match action:
                case EndTurn():
                    self.game_manager.end_turn()
                case MoveAlly(_, ally, target_coord, custom_path):
                    if isinstance(ally, Rodent):
                        self.game_manager.move_rodent(ally, target_coord, custom_path)
                    else:
                        self.game_manager.move_entity_uncheck(ally, target_coord)
                case ActivateSkill(_, entity, skill_index):
                    skill_result = self.game_manager.activate_skill(entity, skill_index)
                    if skill_result == SkillCompleted.CANCELLED:
                        banned_actions.append(action)
                        is_banned_actions_updated = True
                case SelectTargets(skill_targeting, selected_targets):
                    assert self.game_manager.skill_targeting is skill_targeting
                    self.game_manager.apply_skill_callback(list(selected_targets))
                case PlaceSqueak(_, target_coord, hand_index, _):
                    self.game_manager.place_squeak(hand_index, target_coord)
                case _:
                    raise ValueError("action not handled")

    @abstractmethod
    def select_action(self, actions: AIActions) -> AIAction:
        """
        The evaluation function to select the action AI will take from all available actions
        """
        ...

    @abstractmethod
    def get_name_and_description(self) -> tuple[str, str]:
        """
        Return AI's name and description for rendering.
        """
        ...

    def _get_all_actions(self) -> AIActions:
        skill_targeting = self.game_manager.skill_targeting
        if skill_targeting is not None:
            return self.__get_selecting_target_actions(skill_targeting)
        return self.__get_non_selecting_target_actions()

    def __get_selecting_target_actions(
        self, skill_targeting: SkillTargeting
    ) -> AIActions:
        all_actions = AIActions()
        # SelectTarget
        for targets in combinations(
            skill_targeting.available_targets, skill_targeting.target_count
        ):
            all_actions.select_targets.append(SelectTargets(skill_targeting, targets))
        return all_actions

    def __get_non_selecting_target_actions(self) -> AIActions:
        all_actions = AIActions()
        all_actions.end_turn.append(EndTurn())
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
                all_actions.move_ally.append(
                    MoveAlly(ally.move_cost, ally, move_target_coord)
                )
        # ActivateSkill
        for entity in chain(cache.sides[self.ai_side], cache.sides[None]):
            if entity.skill_stamina is not None and entity.skill_stamina <= 0:
                continue
            for i, skill in enumerate(entity.skills):
                if self.game_manager.crumbs < skill.crumb_cost:
                    continue
                all_actions.activate_skill.append(
                    ActivateSkill(skill.crumb_cost, entity, i)
                )
        # PlaceSqueak
        for hand_index, squeak in enumerate(self.game_manager.hands[self.ai_side]):
            if self.game_manager.crumbs < squeak.crumb_cost:
                continue
            for target_coord in squeak.get_placable_tiles(self.game_manager):
                all_actions.place_squeak.append(
                    PlaceSqueak(squeak.crumb_cost, target_coord, hand_index, squeak)
                )
        return all_actions
