from typing import TYPE_CHECKING

from ...feature import Feature
from ...source_of_damage_or_heal import SourceOfDamageOrHeal
from ...effects.global_rodent_effects import MoraleBoost
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
from .common_skills import SelectTarget, TargetAction

if TYPE_CHECKING:
    from ...game_manager import GameManager


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
    description="Live with honor and die with honor. Army marches on its stomach. It'll continue to distribute these supplies until it has drawn its last breath.",
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
            name="My Body",
            method_name="my_body",
            reach=1,
            altitude=10,
            crumb_cost=3,
            tags=[],
        ),
        EntitySkill(
            name="My Heart",
            method_name="my_heart",
            reach=1,
            altitude=1,
            crumb_cost=10,
            tags=[],
        ),
        EntitySkill(
            name="My Soul",
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
        return (
            SelectTarget(self, skill_index=0)
            .can_select_ally_entity()
            .add_target_action(
                TargetAction(self)
                .acquire_ally_entity()
                .apply_effect(MoraleBoost, duration=2)
            )
            .to_skill_targeting(game_manager)
        )

    @entity_skill_check
    def my_heart(self, game_manager: "GameManager") -> SkillTargeting:
        return (
            SelectTarget(self, skill_index=1)
            .can_select_ally_entity()
            .add_target_action(
                TargetAction(self).acquire_ally_entity().heal(self.attack)
            )
            .to_skill_targeting(game_manager)
        )

    @entity_skill_check
    def my_soul(self, game_manager: "GameManager") -> SkillResult:
        if self.my_soul_target is not None and self.my_soul_target.health != 0:
            TargetAction(self).aoe(2).acquire_enemy().damage(self.attack).run(
                game_manager, [self.my_soul_target.pos]
            )
            game_manager.damage_entity(self, INSTANT_KILL, self)
            return SkillCompleted.SUCCESS

        return (
            SelectTarget(self, skill_index=2)
            .can_select_ally_entity(with_hp=False)
            .add_target_action(
                TargetAction(self)
                .acquire_ally_entity()
                .apply_effect(QuartermasterSoul, duration=None)
                .custom_action(self.assign_my_soul_target)
            )
            .to_skill_targeting(game_manager)
        )

    def assign_my_soul_target(
        self,
        game_manager: "GameManager",
        target: Entity | Feature,
        source: SourceOfDamageOrHeal,
    ) -> SkillResult:
        assert isinstance(target, Entity)
        self.my_soul_target = target
        return SkillCompleted.SUCCESS

    def skill_descriptions(self) -> list[str]:
        return [
            'Boost an ally\'s morale by giving them "Morale Boost" status effect increasing its attack by 1 for 3 of ally turns.',
            f"Distribute food to an ally healing it by {self.attack}(ATK) HP.",
            f'Its last breath has come. Give "Quartermaster\'s Soul" status effect to an ally rodent. When activated again, said rodent will deal {self.attack}(ATK) damage to all enemy within 2-tile radius and this rodent will then be defeated. Current target: {"None" if self.my_soul_target is None else f"{self.my_soul_target.name} at {self.my_soul_target.pos}"}',
        ]
