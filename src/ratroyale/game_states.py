from abc import ABC
from dataclasses import dataclass
from enum import Enum

from .backend.game_manager import GameManager


@dataclass
class GameState(ABC):
    pass


@dataclass
class GamePlay(GameState):
    game_manager: GameManager


class MainMenu(GameState):
    pass
