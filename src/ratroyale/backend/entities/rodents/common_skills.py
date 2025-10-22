from typing import TYPE_CHECKING, Callable, Iterable, Self, TypeAlias

from ratroyale.backend.entities.rodent import Rodent
from ratroyale.backend.entity import Entity, SkillCompleted, SkillResult, SkillTargeting
from ratroyale.backend.entity_effect import EntityEffect
from ratroyale.backend.feature import Feature
from ratroyale.backend.hexagon import OddRCoord
from ratroyale.backend.instant_kill import InstantKill
from ratroyale.backend.skill_callback import SkillCallback, skill_callback_check
from ratroyale.backend.source_of_damage_or_heal import SourceOfDamageOrHeal
from ratroyale.backend.tile import Tile
from ratroyale.backend.timer import Timer, TimerCallback, TimerClearSide

if TYPE_CHECKING:
    from ratroyale.backend.game_manager import GameManager

Target: TypeAlias = Entity | Feature

CanSelectCallback = Callable[["GameManager", Tile], bool]
TargetToCoords = Callable[["GameManager", list[OddRCoord]], list[OddRCoord]]
Acquire = Callable[["GameManager", Tile], Target | None]
CallbackToTarget = Callable[["GameManager", Target, SourceOfDamageOrHeal], SkillResult]
CustomAction = Callable[["GameManager", list[OddRCoord]], SkillResult]


def _single_target(
    game_manager: "GameManager", coords: list[OddRCoord]
) -> list[OddRCoord]:
    return coords


class TargetAction:
    Target: TypeAlias = Entity | Feature

    def __init__(self, source: SourceOfDamageOrHeal) -> None:
        self.source = source
        self.target_to_coords: TargetToCoords = _single_target
        self.acquires: list[Acquire] = []
        self.callbacks_to_target: list[CallbackToTarget] = []

    @staticmethod
    def merge(
        target_actions: Iterable["TargetAction" | CustomAction],
        source: SourceOfDamageOrHeal,
    ) -> SkillCallback:
        @skill_callback_check
        def callback(
            game_manager: "GameManager", selected_targets: list["OddRCoord"]
        ) -> SkillResult:
            skill_results: list[SkillResult] = []
            for target_action in target_actions:
                if isinstance(target_action, TargetAction):
                    skill_callback = target_action.build_skill_callback()
                    skill_result = skill_callback(game_manager, selected_targets)
                    skill_results.append(skill_result)
                else:
                    skill_results.append(target_action(game_manager, selected_targets))

            for skill_result in skill_results[:-1]:
                if skill_result != SkillCompleted.SUCCESS:
                    raise ValueError("SkillResult is not success in a chain")
            return skill_results[-1]

        return callback

    def run(
        self, game_manager: "GameManager", selected_targets: list[OddRCoord]
    ) -> None:
        self.build_skill_callback()(game_manager, selected_targets)

    def build_skill_callback(self) -> SkillCallback:
        if len(self.acquires) == 0:
            raise ValueError("TargetAction without acquires is useless")

        @skill_callback_check
        def callback(
            game_manager: "GameManager", selected_targets: list["OddRCoord"]
        ) -> SkillResult:
            selected_targets = self.target_to_coords(game_manager, selected_targets)
            skill_results: list[SkillResult] = []
            for selected_target in selected_targets:
                tile = game_manager.board.get_tile(selected_target)
                if tile is None:
                    continue
                target: Target | None = None
                for acquire in self.acquires:
                    target = acquire(game_manager, tile)
                    if target is not None:
                        break
                if target is None:
                    continue
                if target.is_dead:
                    continue
                for callback_to_target in self.callbacks_to_target:
                    result = callback_to_target(game_manager, target, self.source)
                    skill_results.append(result)
                    if target.is_dead:
                        break
            if not skill_results:
                return SkillCompleted.CANCELLED
            for skill_result in skill_results[:-1]:
                if skill_result != SkillCompleted.SUCCESS:
                    raise ValueError("SkillResult is not success in a chain")
            return skill_results[-1]

        return callback

    def custom_action(self, action: CallbackToTarget) -> Self:
        self.callbacks_to_target.append(action)
        return self

    def damage(self, damage: int | InstantKill) -> Self:
        def callback_to_target(
            game_manager: "GameManager",
            target: Entity | Feature,
            source: SourceOfDamageOrHeal,
        ) -> SkillResult:
            if isinstance(target, Entity):
                game_manager.damage_entity(target, damage, source)
            elif isinstance(target, Feature):
                game_manager.damage_feature(target, damage, source)
            return SkillCompleted.SUCCESS

        self.callbacks_to_target.append(callback_to_target)
        return self

    def heal(self, amount: int) -> Self:
        def callback_to_target(
            game_manager: "GameManager",
            target: Entity | Feature,
            source: SourceOfDamageOrHeal,
        ) -> SkillResult:
            if isinstance(target, Entity):
                game_manager.heal_entity(target, amount, source)
            return SkillCompleted.SUCCESS

        self.callbacks_to_target.append(callback_to_target)
        return self

    def apply_effect(
        self,
        effect: type[EntityEffect],
        *,
        duration: int | None,
        intensity: float = 0,
    ) -> Self:
        def callback_to_target(
            game_manager: "GameManager",
            target: Entity | Feature,
            source: SourceOfDamageOrHeal,
        ) -> SkillResult:
            if isinstance(target, Feature):
                return SkillCompleted.SUCCESS
            game_manager.apply_effect(
                effect(target, duration=duration, intensity=intensity)
            )
            return SkillCompleted.SUCCESS

        self.callbacks_to_target.append(callback_to_target)
        return self

    def force_clear_effect(
        self, effect: type[EntityEffect], *, raise_error_if_not_exist: bool = False
    ) -> Self:
        def callback_to_target(
            game_manager: "GameManager",
            target: Entity | Feature,
            source: SourceOfDamageOrHeal,
        ) -> SkillResult:
            if isinstance(target, Feature):
                return SkillCompleted.SUCCESS
            if effect.name not in target.effects:
                if raise_error_if_not_exist:
                    raise ValueError(
                        f"Effect {effect.name} doesn't exist in {target.name}"
                    )
                else:
                    return SkillCompleted.SUCCESS
            game_manager.force_clear_effect(target.effects[effect.name])
            return SkillCompleted.SUCCESS

        self.callbacks_to_target.append(callback_to_target)
        return self

    def apply_timer(
        self,
        timer_clear_side: TimerClearSide,
        *,
        duration: int,
        on_turn_change: TimerCallback | None = None,
        on_timer_over: TimerCallback | None = None,
    ) -> Self:
        def callback_to_target(
            game_manager: "GameManager",
            target: Entity | Feature,
            source: SourceOfDamageOrHeal,
        ) -> SkillResult:
            if isinstance(target, Feature):
                return SkillCompleted.SUCCESS
            game_manager.apply_timer(
                Timer(
                    target,
                    timer_clear_side,
                    duration=duration,
                    on_turn_change=on_turn_change,
                    on_timer_over=on_timer_over,
                ),
            )
            return SkillCompleted.SUCCESS

        self.callbacks_to_target.append(callback_to_target)
        return self

    def acquire_ally_entity(self, with_hp: bool = True) -> Self:
        def acquire(game_manager: "GameManager", tile: Tile) -> Entity | None:
            for entity in reversed(tile.entities):
                if entity.side == game_manager.turn.other_side():
                    continue
                if with_hp and entity.health is None:
                    continue
                return entity
            return None

        self.acquires.append(acquire)
        return self

    def acquire_custom(self, acquire: Acquire) -> Self:
        self.acquires.append(acquire)
        return self

    def acquire_any(self, with_hp: bool = True) -> Self:
        return self.acquire_any_entity(with_hp).acquire_any_feature(with_hp)

    def acquire_any_entity(self, with_hp: bool = True) -> Self:
        def acquire(game_manager: "GameManager", tile: Tile) -> Entity | None:
            for entity in reversed(tile.entities):
                if with_hp and entity.health is None:
                    continue
                return entity
            return None

        self.acquires.append(acquire)
        return self

    def acquire_any_feature(self, with_hp: bool = True) -> Self:
        def acquire(game_manager: "GameManager", tile: Tile) -> Feature | None:
            for feature in reversed(tile.features):
                if with_hp and feature.health is None:
                    continue
                return feature
            return None

        self.acquires.append(acquire)
        return self

    def acquire_enemy_feature(self, with_hp: bool = True) -> Self:
        def acquire(game_manager: "GameManager", tile: Tile) -> Feature | None:
            for feature in reversed(tile.features):
                if feature.side == game_manager.turn:
                    continue
                if with_hp and feature.health is None:
                    continue
                return feature
            return None

        self.acquires.append(acquire)
        return self

    def acquire_enemy_entity(self, with_hp: bool = True) -> Self:
        def acquire(game_manager: "GameManager", tile: Tile) -> Entity | None:
            for entity in reversed(tile.entities):
                if entity.side == game_manager.turn:
                    continue
                if with_hp and entity.health is None:
                    continue
                return entity
            return None

        self.acquires.append(acquire)
        return self

    def acquire_enemy(self) -> Self:
        return self.acquire_enemy_entity().acquire_enemy_feature()

    def acquire_ally_feature(self, with_hp: bool = True) -> Self:
        def acquire(game_manager: "GameManager", tile: Tile) -> Feature | None:
            for feature in reversed(tile.features):
                if feature.side == game_manager.turn.other_side():
                    continue
                if with_hp and feature.health is None:
                    continue
                return feature
            return None

        self.acquires.append(acquire)
        return self

    def aoe(self, radius: int) -> Self:
        def _multi_target(
            game_manager: "GameManager", coords: list[OddRCoord]
        ) -> list[OddRCoord]:
            result_coords: set[OddRCoord] = set()
            for coord in coords:
                selected_tile = game_manager.board.get_tile(coord)
                if selected_tile is None:
                    continue

                def __is_coord_blocked(
                    target_coord: "OddRCoord", source_coord: "OddRCoord"
                ) -> bool:
                    tile = game_manager.board.get_tile(target_coord)
                    if tile is None:
                        return True
                    return tile.height + radius < tile.get_total_height(
                        game_manager.turn
                    )

                for result_coord in coord.get_reachable_coords(
                    radius, __is_coord_blocked, is_include_self=True
                ):
                    result_coords.add(result_coord)
            return list(result_coords)

        self.target_to_coords = _multi_target
        return self


GetAttackableCoords = Callable[["GameManager"], Iterable[OddRCoord]]


class SelectTarget:
    def __init__(
        self, rodent: Rodent, *, skill_index: int, target_count: int = 1
    ) -> None:
        self.rodent = rodent
        self.skill_index = skill_index
        self.target_count = target_count
        self.can_select_callbacks: list[CanSelectCallback] = []
        self.target_actions: list[TargetAction | CustomAction] = []
        self.get_attackable_coords: GetAttackableCoords = self._get_attackable_coords

    def add_target_action(self, target_action: TargetAction) -> Self:
        self.target_actions.append(target_action)
        return self

    def add_custom_action(self, custom_action: CustomAction) -> Self:
        self.target_actions.append(custom_action)
        return self

    def _get_attackable_coords(
        self, game_manager: "GameManager"
    ) -> Iterable[OddRCoord]:
        return game_manager.board.get_attackable_coords(
            self.rodent, self.rodent.skills[self.skill_index]
        )

    def custom_attackable_coords(
        self, get_attackable_coords: GetAttackableCoords
    ) -> Self:
        self.get_attackable_coords = get_attackable_coords
        return self

    def build_targets(self, game_manager: "GameManager") -> list[OddRCoord]:
        if len(self.can_select_callbacks) == 0:
            raise ValueError("SelectTarget without can_select is useless")
        coords = self.get_attackable_coords(game_manager)
        targets: list[OddRCoord] = []
        for coord in coords:
            tile = game_manager.board.get_tile(coord)
            if tile is None:
                continue
            for can_select_callback in self.can_select_callbacks:
                if can_select_callback(game_manager, tile):
                    targets.append(coord)
                    continue
                continue
        return targets

    def to_skill_targeting(
        self, game_manager: "GameManager", *, can_canel: bool = True
    ) -> SkillTargeting:
        targets = self.build_targets(game_manager)
        return SkillTargeting(
            self.target_count,
            self.rodent,
            self.rodent.skills[self.skill_index],
            targets,
            TargetAction.merge(self.target_actions, self.rodent),
            can_canel,
        )

    def can_select_enemy(self, with_hp: bool = True) -> Self:
        return self.can_select_enemy_feature(with_hp).can_select_enemy_entity(with_hp)

    def can_select_custom(self, can_select_callback: CanSelectCallback) -> Self:
        self.can_select_callbacks.append(can_select_callback)
        return self

    def can_select_tile_without_collision(
        self, is_source_entity_collision: bool = True
    ) -> Self:
        def can_select(game_manager: "GameManager", tile: Tile) -> bool:
            return not tile.is_collision(is_source_entity_collision)

        self.can_select_callbacks.append(can_select)
        return self

    def can_select_any_tile(self) -> Self:
        def can_select(game_manager: "GameManager", tile: Tile) -> bool:
            return True

        self.can_select_callbacks.append(can_select)
        return self

    def can_select_ally_entity(self, with_hp: bool = True) -> Self:
        def can_select(game_manager: "GameManager", tile: Tile) -> bool:
            for entity in reversed(tile.entities):
                if entity.side == game_manager.turn.other_side():
                    continue
                if with_hp and entity.health is None:
                    continue
                return True
            return False

        self.can_select_callbacks.append(can_select)
        return self

    def can_select_ally_feature(self, with_hp: bool = True) -> Self:
        def can_select(game_manager: "GameManager", tile: Tile) -> bool:
            for feature in reversed(tile.features):
                if feature.side == game_manager.turn.other_side():
                    continue
                if with_hp and feature.health is None:
                    continue
                return True
            return False

        self.can_select_callbacks.append(can_select)
        return self

    def can_select_enemy_entity(self, with_hp: bool = True) -> Self:
        def can_select(game_manager: "GameManager", tile: Tile) -> bool:
            for entity in reversed(tile.entities):
                if entity.side == game_manager.turn:
                    continue
                if with_hp and entity.health is None:
                    continue
                return True
            return False

        self.can_select_callbacks.append(can_select)
        return self

    def can_select_enemy_feature(self, with_hp: bool = True) -> Self:
        def can_select(game_manager: "GameManager", tile: Tile) -> bool:
            for feature in reversed(tile.features):
                if feature.side == game_manager.turn:
                    continue
                if with_hp and feature.health is None:
                    continue
                return True
            return False

        self.can_select_callbacks.append(can_select)
        return self
