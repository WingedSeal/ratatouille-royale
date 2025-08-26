
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from .entity import SkillResult
    from .game_manager import GameManager
    from .hexagon import OddRCoord


class SkillCallback(Protocol):
    def __call__(self, game_manager: "GameManager", selected_targets: list["OddRCoord"]) -> "SkillResult | None":
        ...


def skill_callback(callback: "SkillCallback") -> "SkillCallback":
    """
    A decorator to check if a function is compatible with SkillCallback
    """
    return callback
