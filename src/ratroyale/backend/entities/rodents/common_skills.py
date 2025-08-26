from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ...game_manager import GameManager
    from ...entities.rodent import Rodent
    from ...entity import EntitySkill, SkillResult
    from ...board import Board
    from ...hexagon import OddRCoord


def select_target(board: "Board", rodent: "Rodent", skill: "EntitySkill", callback: Callable[["GameManager", list["OddRCoord"]], "SkillResult | None"],
                  target_count: int = 1) -> SkillResult:
    coords = board.get_attackable_coords(rodent, skill)
    return SkillResult(target_count, list(coords), callback)
