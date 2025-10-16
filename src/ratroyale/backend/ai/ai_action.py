from dataclasses import dataclass, field
from typing import Sequence

from ..entity import CallableEntitySkill, Entity, SkillTargeting
from ..hexagon import OddRCoord
from ..player_info.squeak import Squeak


@dataclass(frozen=True)
class AIAction:
    crumb_cost: int


@dataclass(frozen=True)
class MoveAlly(AIAction):
    ally: Entity
    target_coord: OddRCoord
    custom_path: list[OddRCoord] | None = None

    def __str__(self) -> str:
        return f"Move {self.ally.name} from {self.ally.pos} to {self.target_coord}."


@dataclass(frozen=True)
class ActivateSkill(AIAction):
    entity: Entity
    skill_index: int

    def get_skill(self) -> CallableEntitySkill:
        return self.entity.skills[self.skill_index]

    def __str__(self) -> str:
        return f"Activate skill {self.skill_index} ({self.get_skill().name}) of {self.entity.name} at {self.entity.pos}"


@dataclass(frozen=True)
class SelectTargets(AIAction):
    """
    AI isn't allowed to cancel skill
    """

    crumb_cost: int = field(default=0, init=False)
    skill_targeting: SkillTargeting
    selected_targets: tuple["OddRCoord", ...]

    def __str__(self) -> str:
        return f"Select {self.skill_targeting.target_count} target(s): {', '.join(str(target) for target in self.selected_targets)}"


@dataclass(frozen=True)
class PlaceSqueak(AIAction):
    target_coord: OddRCoord
    hand_index: int
    squeak: Squeak

    def __str__(self) -> str:
        return (
            f"Place Sqeak {self.hand_index} ({self.squeak.name}) at {self.target_coord}"
        )


@dataclass(frozen=True)
class EndTurn(AIAction):
    crumb_cost: int = field(default=0, init=False)

    def __str__(self) -> str:
        return "End turn"


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
