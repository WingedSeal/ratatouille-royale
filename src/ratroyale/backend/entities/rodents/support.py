from typing import TYPE_CHECKING

from ratroyale.backend.hexagon import OddRCoord
from ratroyale.backend.skill_callback import SkillCallback, skill_callback_check

from ...entity import (
    Entity,
    EntitySkill,
    SkillCompleted,
    SkillResult,
    SkillTargeting,
    entity_skill_check,
)
from ...entity_effect import EffectClearSide, EntityEffect, effect_data
from ...instant_kill import INSTANT_KILL
from ...tags import RodentClassTag
from ..rodent import Rodent, rodent_data
from .common_skills import (
    SelectTargetMode,
    aoe_damage,
    apply_effect,
    normal_heal,
    select_targets,
)

if TYPE_CHECKING:
    from ...game_manager import GameManager


@effect_data(EffectClearSide.ALLY, name="Quartermaster's Body")
class QuartermasterBody(EntityEffect):
    def on_cleared(self, game_manager: "GameManager", *, is_overridden: bool) -> None:
        if not isinstance(self.entity, Rodent):
            return None
        self.entity.attack -= 1

    def on_applied(self, game_manager: "GameManager", *, is_overriding: bool) -> None:
        if not isinstance(self.entity, Rodent):
            return None
        self.entity.attack += 1

    def on_turn_change(self, game_manager: "GameManager") -> None:
        pass

    def effect_descriptions(self) -> str:
        return "Attack increased by 1"


@effect_data(EffectClearSide.ALLY, name="Quartermaster's Soul")
class QuartermasterSoul(EntityEffect):
    def on_cleared(self, game_manager: "GameManager", *, is_overridden: bool) -> None:
        if not isinstance(self.entity, Rodent):
            return None
        self.entity.defense -= 1

    def on_applied(self, game_manager: "GameManager", *, is_overriding: bool) -> None:
        if not isinstance(self.entity, Rodent):
            return None
        self.entity.defense += 1

    def on_turn_change(self, game_manager: "GameManager") -> None:
        pass

    def effect_descriptions(self) -> str:
        return "Someone entrusted their soul"


@rodent_data(
    name="Quartermaster",
    description="Live with honor and die with honor.  Army marches on its stomach. It'll continue to distribute these supplies until it has drawn its last breath.",
    health=5,
    defense=0,
    speed=1,
    move_stamina=2,
    skill_stamina=1,
    attack=10,
    move_cost=20,
    height=0,
    class_tag=RodentClassTag.SUPPORT,
    entity_tags=[],
    skills=[
        EntitySkill(
            name="My body",
            method_name="my_body",
            reach=1,
            altitude=10,
            crumb_cost=3,
            tags=[],
        ),
        EntitySkill(
            name="My heart",
            method_name="my_heart",
            reach=1,
            altitude=1,
            crumb_cost=10,
            tags=[],
        ),
        EntitySkill(
            name="My soul",
            method_name="my_soul",
            reach=3,
            altitude=10,
            crumb_cost=12,
            tags=[],
        ),
    ],
)
class Quartermaster(Rodent):
    my_soul_target: Entity | None = None

    @entity_skill_check
    def my_body(self, game_manager: "GameManager") -> SkillTargeting:
        return select_targets(
            game_manager.board,
            self,
            self.skills[0],
            apply_effect(QuartermasterBody, duration=2),
        )

    @entity_skill_check
    def my_heart(self, game_manager: "GameManager") -> SkillTargeting:
        return select_targets(
            game_manager.board,
            self,
            self.skills[1],
            normal_heal(self.attack, self, is_feature_targetable=False),
            target_mode=SelectTargetMode.ALLY,
        )

    @entity_skill_check
    def my_soul(self, game_manager: "GameManager") -> SkillResult:
        if (
            self.my_soul_target is not None
            and self.my_soul_target in game_manager.board.cache.entities
        ):
            aoe_damage(self.attack, 2, self.my_soul_target, is_stackable=True)
            game_manager.damage_entity(self, INSTANT_KILL, self)
            return SkillCompleted.SUCCESS

        return select_targets(
            game_manager.board,
            self,
            self.skills[2],
            self.my_soul_callback(),
            target_mode=SelectTargetMode.ALLY,
            is_feature_targetable=False,
        )

    def my_soul_callback(self) -> SkillCallback:
        @skill_callback_check
        def skill_callback(
            game_manager: "GameManager", selected_targets: list[OddRCoord]
        ) -> SkillResult:
            apply_effect(QuartermasterSoul, duration=None)(
                game_manager, selected_targets
            )
            self.my_soul_target = game_manager.get_ally_on_pos(
                selected_targets[0], exclude_without_hp=False
            )
            return SkillCompleted.SUCCESS

        return skill_callback
