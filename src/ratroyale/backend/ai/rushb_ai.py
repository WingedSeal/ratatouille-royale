import random
from dataclasses import dataclass
from functools import cmp_to_key, lru_cache

from ..entities.rodent import Rodent
from ..entity import CallableEntitySkill
from ..features.common import Lair
from ..hexagon import OddRCoord
from ..player_info.squeak import SqueakType
from ..tags import SkillTag
from .ai_action import AIAction, AIActions, EndTurn, MoveAlly, PlaceSqueak
from .base_ai import BaseAI


@dataclass
class RodentAndSkill:
    rodent: Rodent
    skill: CallableEntitySkill


class RushBAI(BaseAI):
    """
    Place the cheapest rodent in hand in the nearest deployment zone
    at enemy base. The rush straight to it without regard for its life.
    """

    last_rodent_and_skill_in_lair_range: RodentAndSkill | None = None

    @lru_cache(maxsize=1)
    def choose_lair(self) -> Lair:
        return random.choice(
            self.game_manager.board.cache.lairs[self.ai_side.other_side()]
        )

    @lru_cache(maxsize=1)
    def choose_lair_coord(self) -> OddRCoord:
        return random.choice(self.choose_lair().shape)

    def get_name_and_description(self) -> tuple[str, str]:
        return "RushB", "Your base is not safe."

    def get_ally_on_field(self) -> Rodent | None:
        for entity in self.game_manager.board.cache.sides[self.ai_side]:
            if isinstance(entity, Rodent):
                return entity
        return None

    def compare_hands(self, a: PlaceSqueak, b: PlaceSqueak) -> int:
        if a.crumb_cost != b.crumb_cost:
            return a.crumb_cost - b.crumb_cost
        if a.squeak.rodent is None:
            return 1
        if b.squeak.rodent is None:
            return 1

        a_to_lair = a.target_coord.path_find(
            self.choose_lair_coord(),
            self.game_manager.board._is_coord_blocked(
                a.squeak.rodent.collision, self.ai_side
            ),
        )
        if a_to_lair is None:
            return 1
        b_to_lair = b.target_coord.path_find(
            self.choose_lair_coord(),
            self.game_manager.board._is_coord_blocked(
                b.squeak.rodent.collision, self.ai_side
            ),
        )
        if b_to_lair is None:
            return 1
        return len(a_to_lair) - len(b_to_lair)

    def compare_moves(self, a: MoveAlly, b: MoveAlly) -> int:
        a_to_lair = a.target_coord.path_find(
            self.choose_lair_coord(),
            self.game_manager.board.is_coord_blocked(a.ally),
        )
        if a_to_lair is None:
            return 1
        b_to_lair = b.target_coord.path_find(
            self.choose_lair_coord(),
            self.game_manager.board.is_coord_blocked(b.ally),
        )
        if b_to_lair is None:
            return 1
        return len(a_to_lair) - len(b_to_lair)

    def select_hand(self, hands: list[PlaceSqueak]) -> PlaceSqueak | None:
        sorted_hands = sorted(hands, key=cmp_to_key(self.compare_hands))
        if len(sorted_hands) == 0:
            return None
        for hand in sorted_hands:
            if hand.squeak.squeak_type != SqueakType.RODENT:
                continue
            assert hand.squeak.rodent is not None
            rodent = hand.squeak.rodent
            for skill in rodent.skills:
                if SkillTag.NO_TARGET_FEATURE not in skill.tags:
                    return hand
        return sorted_hands[0]

    def select_action(self, actions: AIActions) -> AIAction:
        if self.game_manager.is_selecting_target:
            for select_targets in actions.select_targets:
                if self.choose_lair_coord() in select_targets.selected_targets:
                    return select_targets
            return actions.select_targets[0]

        ally_on_field = self.get_ally_on_field()
        # If there's no ally on field, place squeak.
        if ally_on_field is None:
            hand = self.select_hand(actions.place_squeak)
            if hand is None:
                return EndTurn()
            return hand

        # If there was already a rodent ready to attack the lair, just use the same skill.
        if (
            self.last_rodent_and_skill_in_lair_range is not None
            and ally_on_field is self.last_rodent_and_skill_in_lair_range.rodent
        ):
            for activate_skill in actions.activate_skill:
                if activate_skill.entity is not ally_on_field:
                    continue
                assert isinstance(activate_skill.entity, Rodent)
                skill = activate_skill.get_skill()
                if skill is self.last_rodent_and_skill_in_lair_range.skill:
                    return activate_skill
        self.last_rodent_and_skill_in_lair_range = None

        # Check if lair is now within range
        for activate_skill in actions.activate_skill:
            if activate_skill.entity is not ally_on_field:
                continue
            assert isinstance(activate_skill.entity, Rodent)
            skill = activate_skill.get_skill()
            if (
                self.choose_lair_coord()
                in self.game_manager.board.get_attackable_coords(ally_on_field, skill)
            ):
                self.last_rodent_and_skill_in_lair_range = RodentAndSkill(
                    ally_on_field, skill
                )
                return activate_skill

        # Move rodent to enemy lair
        # if not actions.move_ally:
        #     return EndTurn()
        best_move = max(actions.move_ally, key=cmp_to_key(self.compare_moves))
        return best_move
