from enum import Enum, auto
from typing import TYPE_CHECKING, Iterable

from ...side import Side
from ...entities.rodent import Rodent
from ...entity import Entity, SkillCompleted, SkillResult, SkillTargeting
from ...entity_effect import EntityEffect
from ...error import InvalidMoveTargetError, ShortHandSkillCallbackError
from ...skill_callback import SkillCallback, skill_callback_check
from ...source_of_damage_or_heal import SourceOfDamageOrHeal
from ...timer import Timer, TimerCallback, TimerClearSide
from ...hexagon import OddRCoord

if TYPE_CHECKING:
    from ...board import Board
    from ...entity import CallableEntitySkill
    from ...game_manager import GameManager


class SelectTargetMode(Enum):
    ENEMY_WITH_HP = auto()
    ENEMY = auto()
    ALLY = auto()
    ANY = auto()
    """Any entity or feature (if is_feature_targetable is True)"""
    ANY_TILE = auto()


def filter_targetable_coords(
    coords: Iterable[OddRCoord],
    board: "Board",
    side: Side | None,
    target_mode: SelectTargetMode = SelectTargetMode.ENEMY_WITH_HP,
    is_feature_targetable: bool = True,
) -> list[OddRCoord]:
    targets: list[OddRCoord] = []
    for coord in coords:
        tile = board.get_tile(coord)
        if tile is None:
            continue
        match target_mode:
            case SelectTargetMode.ANY_TILE:
                targets.append(coord)
            case SelectTargetMode.ANY:
                if tile.entities:
                    targets.append(coord)
                    continue
                if is_feature_targetable and tile.features:
                    targets.append(coord)
                    continue
            case SelectTargetMode.ENEMY_WITH_HP:
                if any(
                    entity.side != side and entity.health is not None
                    for entity in tile.entities
                ):
                    targets.append(coord)
                    continue
                if is_feature_targetable and any(
                    feature.side != side and feature.health is not None
                    for feature in tile.features
                ):
                    targets.append(coord)
                    continue
            case SelectTargetMode.ENEMY:
                if any(entity.side != side for entity in tile.entities):
                    targets.append(coord)
                    continue
                if is_feature_targetable and any(
                    feature.side != side for feature in tile.features
                ):
                    targets.append(coord)
                    continue
            case SelectTargetMode.ALLY:
                if any(entity.side == side for entity in tile.entities):
                    targets.append(coord)
                    continue
                if is_feature_targetable and any(
                    feature.side == side for feature in tile.features
                ):
                    targets.append(coord)
                    continue
    return targets


def select_targets(
    board: "Board",
    rodent: "Rodent",
    skill: "CallableEntitySkill",
    callback: "SkillCallback" | Iterable["SkillCallback"],
    target_count: int = 1,
    *,
    is_feature_targetable: bool = True,
    target_mode: SelectTargetMode = SelectTargetMode.ENEMY_WITH_HP,
    can_cancel: bool = True,
) -> SkillTargeting:

    @skill_callback_check
    def skill_callback(
        game_manager: "GameManager", selected_targets: list[OddRCoord]
    ) -> SkillResult:
        if isinstance(callback, Iterable):
            for c in callback:
                result_enum = c(game_manager, selected_targets)
                if result_enum != SkillCompleted.SUCCESS:
                    raise ShortHandSkillCallbackError(
                        f"{select_targets.__name__} is used with shorthand callback (iterable of callback) but one of them didn't succeed instantly."
                    )
            return SkillCompleted.SUCCESS
        return callback(game_manager, selected_targets)

    coords = board.get_attackable_coords(rodent, skill)
    targets = filter_targetable_coords(
        coords, board, rodent.side, target_mode, is_feature_targetable
    )
    return SkillTargeting(
        target_count, rodent, skill, targets, skill_callback, can_cancel
    )


def move(self: Entity, *, custom_jump_height: int | None = None) -> SkillCallback:
    @skill_callback_check
    def callback(
        game_manager: "GameManager", selected_targets: list[OddRCoord]
    ) -> SkillCompleted:
        if len(selected_targets) != 1:
            raise ValueError("Multiple targets for teleport.")
        try:
            game_manager.move_entity_uncheck(
                self, selected_targets[0], custom_jump_height=custom_jump_height
            )
        except InvalidMoveTargetError:
            return SkillCompleted.CANCELLED
        return SkillCompleted.SUCCESS

    return callback


def normal_damage(
    damage: int, source: SourceOfDamageOrHeal, *, is_feature_targetable: bool = True
) -> SkillCallback:
    """
    Apply normal damage
    :param damage: Damage to deal
    """

    @skill_callback_check
    def callback(
        game_manager: "GameManager", selected_targets: list[OddRCoord]
    ) -> SkillCompleted:
        for target in selected_targets:
            enemy = game_manager.get_enemy_on_pos(target)
            if enemy is not None:
                game_manager.damage_entity(enemy, damage, source)
                continue
            if not is_feature_targetable:
                return SkillCompleted.SUCCESS
            feature = game_manager.get_feature_on_pos(target)
            if feature is None:
                return SkillCompleted.SUCCESS
            game_manager.damage_feature(feature, damage, source)
        return SkillCompleted.SUCCESS

    return callback


def normal_heal(
    heal: int, source: SourceOfDamageOrHeal, *, is_feature_targetable: bool = False
) -> SkillCallback:
    """
    Apply normal heal
    :param heal: Amount to heal
    """

    @skill_callback_check
    def callback(
        game_manager: "GameManager", selected_targets: list[OddRCoord]
    ) -> SkillCompleted:
        for target in selected_targets:
            ally = game_manager.get_ally_on_pos(target)
            if ally is not None:
                game_manager.heal_entity(ally, heal, source)
                continue
            if not is_feature_targetable:
                raise ValueError("Trying to damage entity that is not there")
            feature = game_manager.get_ally_feature_on_pos(target)
            if feature is None:
                raise ValueError("Trying to damage nothing")
            game_manager.damage_feature(feature, heal, source)
        return SkillCompleted.SUCCESS

    return callback


def apply_timer(
    timer_clear_side: TimerClearSide,
    *,
    duration: int,
    on_turn_change: TimerCallback | None = None,
    on_timer_over: TimerCallback | None = None,
    is_ally_instead: bool = False,
) -> SkillCallback:
    """
    Apply timer on enemy (or ally if `is_ally_instead`) rodent
    :is_ally_instead: Target ally instead of enemy
    """

    @skill_callback_check
    def callback(
        game_manager: "GameManager", selected_targets: list[OddRCoord]
    ) -> SkillCompleted:
        for target in selected_targets:
            if is_ally_instead:
                entity = game_manager.get_ally_on_pos(target)
            else:
                entity = game_manager.get_enemy_on_pos(target)
            if entity is None:
                return SkillCompleted.SUCCESS
            game_manager.apply_timer(
                Timer(
                    entity,
                    timer_clear_side,
                    duration=duration,
                    on_turn_change=on_turn_change,
                    on_timer_over=on_timer_over,
                ),
            )
        return SkillCompleted.SUCCESS

    return callback


def apply_effect(
    effect: type[EntityEffect],
    *,
    duration: int | None,
    intensity: float = 0,
    is_ally_instead: bool = False,
    stack_intensity: bool = False,
) -> SkillCallback:
    """
    Apply effect on enemy (or ally if `is_ally_instead`) rodent
    :param effect: EntityEffect to apply to enemy
    :is_ally_instead: Target ally instead of enemy
    :stack_intensity: Whether to stack intensity and extend the duration instead (Note that it'll not recall on_apply)
    """

    @skill_callback_check
    def callback(
        game_manager: "GameManager", selected_targets: list[OddRCoord]
    ) -> SkillCompleted:
        for target in selected_targets:
            if is_ally_instead:
                entity = game_manager.get_ally_on_pos(target)
            else:
                entity = game_manager.get_enemy_on_pos(target)
            if entity is None:
                return SkillCompleted.SUCCESS
            game_manager.apply_effect(
                effect(entity, duration=duration, intensity=intensity),
                stack_intensity=stack_intensity,
            )
        return SkillCompleted.SUCCESS

    return callback


def aoe_damage(
    damage: int,
    radius: int,
    source: SourceOfDamageOrHeal,
    *,
    is_stackable: bool = False,
    is_feature_targetable: bool = True,
    is_friendly_fire: bool = False,
) -> SkillCallback:
    """
    Deal aoe damage
    :param damage: Damage to deal
    :param radius: Radius of the aoe damage, this number is also altitude for checking line of sight
    :param is_stackable: Whether the same tile should get hit multiple times when selected area overlaps,
        defaults to `False`
    :param is_friendly_fire: Whether the damage also affect ally
    :returns: SkillCallback
    """

    @skill_callback_check
    def callback(
        game_manager: "GameManager", selected_targets: list[OddRCoord]
    ) -> SkillCompleted:
        tagged_coord: set[OddRCoord] = set()
        for selected_target in selected_targets:
            selected_tile = game_manager.board.get_tile(selected_target)
            if selected_tile is None:
                raise ValueError("Invalid Tile was selected")
            selected_tile_ = selected_tile

            def __is_coord_blocked(
                target_coord: OddRCoord, source_coord: OddRCoord
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
                if is_friendly_fire:
                    enemy = game_manager.get_both_side_on_pos(coord)
                else:
                    enemy = game_manager.get_enemy_on_pos(coord)
                if enemy is not None:
                    game_manager.damage_entity(enemy, damage, source)
                    continue
                if not is_feature_targetable:
                    raise ValueError("Trying to damage entity that is not there")
                feature = game_manager.get_feature_on_pos(coord)
                if feature is not None:
                    game_manager.damage_feature(feature, damage, source)
                if not is_stackable:
                    tagged_coord.add(coord)
        return SkillCompleted.SUCCESS

    return callback
