from abc import ABC
from dataclasses import dataclass

from ratroyale.backend.entity import SkillResult

from .backend.hexagon import OddRCoord
from .backend.game_manager import GameManager


@dataclass
class GameState(ABC):
    pass


@dataclass
class GamePlay(GameState):
    game_manager: GameManager


@dataclass
class SelectTarget(GameState):
    targets: list[OddRCoord]
    skill_result: SkillResult


class MainMenu(GameState):
    pass
