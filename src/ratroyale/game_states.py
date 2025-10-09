from abc import ABC
from dataclasses import dataclass

from .backend.entity import SkillTargeting
from .backend.game_manager import GameManager
from .backend.hexagon import OddRCoord


@dataclass
class GameState(ABC):
    pass


@dataclass
class GamePlay(GameState):
    game_manager: GameManager


@dataclass
class SelectTarget(GameState):
    targets: list[OddRCoord]
    skill_result: SkillTargeting


class MainMenu(GameState):
    pass
