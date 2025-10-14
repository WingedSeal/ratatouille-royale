from typing import TYPE_CHECKING, Iterable

from ratroyale.backend.error import ShortHandSkillCallbackError

from ...entity import SkillCompleted, SkillResult, SkillTargeting
from ...entity_effect import EntityEffect
from ...skill_callback import SkillCallback, skill_callback_check

if TYPE_CHECKING:
    from ...board import Board
    from ...entities.rodent import Rodent
    from ...entity import CallableEntitySkill
    from ...game_manager import GameManager
    from ...hexagon import OddRCoord


def select_any_tile(
    board: "Board",
    rodent: "Rodent",
    skill: "CallableEntitySkill",
    callback: "SkillCallback",
    target_count: int = 1,
    *,
    can_cancel: bool = True,
) -> SkillTargeting:
    coords = board.get_attackable_coords(rodent, skill)
    return SkillTargeting(
        target_count, rodent, skill, list(coords), callback, can_cancel
    )


def select_targetable(
    board: "Board",
    rodent: "Rodent",
    skill: "CallableEntitySkill",
    callback: "SkillCallback" | Iterable["SkillCallback"],
    target_count: int = 1,
    *,
    is_feature_targetable: bool = True,
    can_cancel: bool = True,
) -> SkillTargeting:

    @skill_callback_check
    def skill_callback(
        game_manager: "GameManager", selected_targets: list["OddRCoord"]
    ) -> SkillResult:
        if isinstance(callback, Iterable):
            for c in callback:
                result_enum = c(game_manager, selected_targets)
                if result_enum != SkillCompleted.SUCCESS:
                    raise ShortHandSkillCallbackError(
                        f"{select_targetable.__name__} is used with shorthand callback (iterable of callback) but one of them didn't succeed instantly."
                    )
            return SkillCompleted.SUCCESS
        return callback(game_manager, selected_targets)

    coords = board.get_attackable_coords(rodent, skill)
    targets: list[OddRCoord] = []
    for coord in coords:
        tile = board.get_tile(coord)
        if tile is None:
            continue
        if any(
            entity.side != rodent.side and entity.health is not None
            for entity in tile.entities
        ):
            targets.append(coord)
            continue
        if is_feature_targetable and any(
            feature.side != rodent.side and feature.health is not None
            for feature in tile.features
        ):
            targets.append(coord)
            continue
    return SkillTargeting(
        target_count, rodent, skill, targets, skill_callback, can_cancel
    )


def normal_damage(damage: int, *, is_feature_targetable: bool = True) -> SkillCallback:
    """
    Apply normal damage
    :param damage: Damage to deal
    """

    @skill_callback_check
    def callback(
        game_manager: "GameManager", selected_targets: list["OddRCoord"]
    ) -> SkillCompleted:
        for target in selected_targets:
            enemy = game_manager.get_enemy_on_pos(target)
            if enemy is not None:
                game_manager.board.damage_entity(enemy, damage)
                continue
            if not is_feature_targetable:
                raise ValueError("Trying to damage entity that is not there")
            feature = game_manager.get_feature_on_pos(target)
            if feature is None:
                raise ValueError("Trying to damage nothing")
            game_manager.board.damage_feature(feature, damage)
        return SkillCompleted.SUCCESS

    return callback


def apply_effect(
    effect: type[EntityEffect],
    *,
    duration: int | None,
    intensity: float,
    is_ally_instead: bool = False,
) -> SkillCallback:
    """
    Apply effect on enemy (or ally if `is_ally_instead`) rodent
    :param effect: EntityEffect to apply to enemy
    :is_ally_instead: Target ally instead of enemy
    """

    @skill_callback_check
    def callback(
        game_manager: "GameManager", selected_targets: list["OddRCoord"]
    ) -> SkillCompleted:
        for target in selected_targets:
            if is_ally_instead:
                entity = game_manager.get_ally_on_pos(target)
            else:
                entity = game_manager.get_enemy_on_pos(target)
            assert entity is not None
            game_manager.apply_effect(
                entity, effect(entity, duration=duration, intensity=intensity)
            )
        return SkillCompleted.SUCCESS

    return callback


def aoe_damage(
    damage: int,
    radius: int,
    *,
    is_stackable: bool = False,
    is_feature_targetable: bool = True,
) -> SkillCallback:
    """
    Deal aoe damage
    :param damage: Damage to deal
    :param radius: Radius of the aoe damage, this number is also altitude for checking line of sight
    :param is_stackable: Whether the same tile should get hit multiple times when selected area overlaps,
        defaults to `False`
    :returns: SkillCallback
    """

    @skill_callback_check
    def callback(
        game_manager: "GameManager", selected_targets: list["OddRCoord"]
    ) -> SkillCompleted:
        tagged_coord: set["OddRCoord"] = set()
        for selected_target in selected_targets:
            selected_tile = game_manager.board.get_tile(selected_target)
            if selected_tile is None:
                raise ValueError("Invalid Tile was selected")
            selected_tile_ = selected_tile

            def __is_coord_blocked(
                target_coord: "OddRCoord", source_coord: "OddRCoord"
            ) -> bool:
                tile = game_manager.board.get_tile(target_coord)
                if tile is None:
                    return True
                return selected_tile_.height + radius < tile.get_total_height(
                    game_manager.turn
                )

            for coord in selected_target.get_reachable_coords(
                radius, __is_coord_blocked, is_include_self=True
            ):
                if not is_stackable and coord in tagged_coord:
                    continue
                enemy = game_manager.get_enemy_on_pos(coord)
                if enemy is not None:
                    game_manager.board.damage_entity(enemy, damage)
                    continue
                if not is_feature_targetable:
                    raise ValueError("Trying to damage entity that is not there")
                feature = game_manager.get_feature_on_pos(coord)
                if feature is None:
                    raise ValueError("Trying to damage nothing")
                game_manager.board.damage_feature(feature, damage)
                if not is_stackable:
                    tagged_coord.add(coord)
        return SkillCompleted.SUCCESS

    return callback
