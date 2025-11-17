from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ratroyale.backend.side import Side

from ..hexagon import OddRCoord
from ..feature import Feature

if TYPE_CHECKING:
    from ..entity import Entity
    from ..game_manager import GameManager


@dataclass
class Lair(Feature):
    @staticmethod
    def FEATURE_ID() -> int:
        return 1

    @staticmethod
    def is_collision() -> bool:
        return True

    @staticmethod
    def get_name_and_description() -> tuple[str, str]:
        return "Lair", "Your base. If its health goes down to 0, you lose."


@dataclass
class DeploymentZone(Feature):
    @staticmethod
    def FEATURE_ID() -> int:
        return 2

    @staticmethod
    def is_collision() -> bool:
        return False

    @staticmethod
    def get_name_and_description() -> tuple[str, str]:
        return "Deployment Zone", "Places for summoning"


@dataclass
class CrumbsStack(Feature):
    side_count: dict[Side, int] = field(
        default_factory=lambda: defaultdict(int), init=False, repr=False
    )

    @staticmethod
    def FEATURE_ID() -> int:
        return 3

    @staticmethod
    def is_collision() -> bool:
        return False

    @staticmethod
    def get_name_and_description() -> tuple[str, str]:
        return (
            "Crumbs Stack",
            "Gain +10% crumbs per turn if one ally or more is standing on it.",
        )

    def on_entity_enter(
        self,
        game_manager: "GameManager",
        entity: "Entity",
        coord_that_entity_enter: OddRCoord,
    ) -> None:
        if entity.side is None:
            return
        if self.side_count[entity.side] == 0:
            game_manager.crumbs_per_turn_modifier.multiplier[entity.side] += 0.1
        self.side_count[entity.side] += 1

    def on_entity_exit(
        self,
        game_manager: "GameManager",
        entity: "Entity",
        coord_that_entity_exit: OddRCoord | None,
    ) -> None:
        if entity.side is None:
            return
        self.side_count[entity.side] -= 1
        if self.side_count[entity.side] == 0:
            game_manager.crumbs_per_turn_modifier.multiplier[entity.side] -= 0.1
