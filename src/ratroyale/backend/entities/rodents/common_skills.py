from typing import TYPE_CHECKING


from ...skill_callback import SkillCallback, skill_callback_check


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


def select_targetable(board: "Board", rodent: "Rodent", skill: "EntitySkill", callback: "SkillCallback", target_count: int = 1, *, is_feature_targetable: bool = True):
    coords = board.get_attackable_coords(rodent, skill)
    targets = []
    for coord in coords:
        tile = board.get_tile(coord)
        if tile is None:
            continue
        if any(entity.side != rodent.side and entity.health is not None for entity in tile.entities):
            targets.append(coord)
            continue
        if any(feature.side != rodent.side and feature.health is not None for feature in tile.features):
            targets.append(coord)
            continue
    return SkillResult(target_count, targets, callback)


def normal_damage(damage: int) -> SkillCallback:
    """
    Apply normal damage
    :param damage: Damage to deal
    """
    @skill_callback_check
    def callback(game_manager: "GameManager", selected_targets: list["OddRCoord"]) -> None:
        for target in selected_targets:
            game_manager.board.damage_entity(
                game_manager.get_enemy_on_pos(target), damage)
    return callback


def aoe_damage(damage: int, radius: int, *, is_stackable: bool = False) -> SkillCallback:
    """
    Deal aoe damage
    :param damage: Damage to deal
    :param radius: Radius of the aoe damage, this number is also altitude for checking line of sight
    :param is_stackable: Whether the same tile should get hit multiple times when selected area overlaps, 
        defaults to `False`
    :returns: SkillCallback
    """
    @skill_callback_check
    def callback(game_manager: "GameManager", selected_targets: list["OddRCoord"]) -> None:
        tagged_coord: set["OddRCoord"] = set()
        for selected_target in selected_targets:
            selected_tile = game_manager.board.get_tile(selected_target)
            if selected_tile is None:
                raise ValueError("Invalid Tile was selected")
            selected_tile_ = selected_tile

            def __is_coord_blocked(target_coord: "OddRCoord", source_coord: "OddRCoord") -> bool:
                tile = game_manager.board.get_tile(target_coord)
                if tile is None:
                    return True
                return selected_tile_.height + radius < tile.get_total_height(game_manager.turn)
            for coord in selected_target.get_reachable_coords(radius, __is_coord_blocked, is_include_self=True):
                if not is_stackable and coord in tagged_coord:
                    continue
                game_manager.board.damage_entity(
                    game_manager.get_enemy_on_pos(coord), damage)
                if not is_stackable:
                    tagged_coord.add(coord)
    return callback
