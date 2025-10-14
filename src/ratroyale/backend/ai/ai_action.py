from dataclasses import dataclass, field

from ..entity import Entity, SkillTargeting
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


@dataclass(frozen=True)
class ActivateSkill(AIAction):
    entity: Entity
    skill_index: int


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
