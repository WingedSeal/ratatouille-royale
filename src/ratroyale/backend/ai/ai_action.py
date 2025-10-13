from dataclasses import dataclass, field
from typing import Sequence

from ..player_info.squeak import Squeak
from ..entity import CallableEntitySkill, Entity, SkillTargeting
from ..hexagon import OddRCoord


@dataclass(frozen=True)
class AIAction:
    crumb_cost: int


@dataclass(frozen=True)
class MoveAlly(AIAction):
    ally: Entity
    target_coord: OddRCoord
    custom_path: list[OddRCoord] | None = None


@dataclass(frozen=True)
class ActivateSkill(AIAction):
    entity: Entity
    skill_index: int

    def get_skill(self) -> CallableEntitySkill:
        return self.entity.skills[self.skill_index]


@dataclass(frozen=True)
class SelectTargets(AIAction):
    """
    AI isn't allowed to cancel skill
    """

    crumb_cost: int = field(default=0, init=False)
    skill_targeting: SkillTargeting
    selected_targets: tuple["OddRCoord", ...]


@dataclass(frozen=True)
class PlaceSqueak(AIAction):
    target_coord: OddRCoord
    hand_index: int
    squeak: Squeak


@dataclass(frozen=True)
class EndTurn(AIAction):
    crumb_cost: int = field(default=0, init=False)


class AIActions:
    def __init__(self) -> None:
        self.move_ally: list[MoveAlly] = []
        self.activate_skill: list[ActivateSkill] = []
        self.select_targets: list[SelectTargets] = []
        self.place_squeak: list[PlaceSqueak] = []
        self.end_turn: list[EndTurn] = []

    def flattern(self) -> Sequence[AIAction]:
        return (
            self.move_ally
            + self.activate_skill
            + self.select_targets
            + self.place_squeak
            + self.end_turn
        )
