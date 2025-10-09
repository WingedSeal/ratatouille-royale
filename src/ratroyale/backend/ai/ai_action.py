from dataclasses import dataclass, field

from ..hexagon import OddRCoord

from ..entity import Entity, SkillTargeting


@dataclass
class AIAction:
    crumb_cost: int


@dataclass
class MoveAlly(AIAction):
    ally: Entity
    target_coord: OddRCoord
    custom_path: list[OddRCoord] | None = None


@dataclass
class ActivateSkill(AIAction):
    entity: Entity
    skill_index: int


@dataclass
class SelectTargets(AIAction):
    """
    AI isn't allowed to cancel skill
    """

    crumb_cost: int = field(default=0, init=False)
    skill_targeting: SkillTargeting
    selected_targets: tuple["OddRCoord", ...]


@dataclass
class EndTurn(AIAction):
    crumb_cost: int = field(default=0, init=False)
