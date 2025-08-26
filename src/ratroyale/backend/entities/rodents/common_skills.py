from typing import TYPE_CHECKING

from ...skill_callback import SkillCallback, skill_callback


if TYPE_CHECKING:
    from ...game_manager import GameManager
    from ...entities.rodent import Rodent
    from ...entity import EntitySkill, SkillResult
    from ...board import Board
    from ...hexagon import OddRCoord


def select_any_tile(board: "Board", rodent: "Rodent", skill: "EntitySkill", callback: "SkillCallback",
                    target_count: int = 1) -> SkillResult:
    coords = board.get_attackable_coords(rodent, skill)
    return SkillResult(target_count, list(coords), callback)


def select_enemy_rodent(board: "Board", rodent: "Rodent", skill: "EntitySkill", callback: "SkillCallback", target_count: int = 1):
    pass


@skill_callback
def normal_damage(game_manager: "GameManager", selected_targets: list["OddRCoord"]) -> None:
    pass
