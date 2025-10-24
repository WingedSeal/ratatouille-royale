import random
from typing import TYPE_CHECKING

from .common_skills import SelectTarget, TargetAction
from ...entity_effect import EffectClearSide, EntityEffect, effect_data
from ...hexagon import OddRCoord
from ...instant_kill import InstantKill
from ...source_of_damage_or_heal import SourceOfDamageOrHeal
from ...entity import (
    Entity,
    EntitySkill,
    SkillCompleted,
    SkillResult,
    SkillTargeting,
    entity_skill_check,
)
from ...tags import EntityTag, RodentClassTag
from ..rodent import Rodent, rodent_data

if TYPE_CHECKING:
    from ...game_manager import GameManager


@rodent_data(
    name="Mayo",
    description="With its mighty sqeeze bottle, sky's the limit. It can achieve unrivaled mobility. Its attack, however, is sub-optimal. ",
    health=10,
    defense=2,
    speed=10,
    move_stamina=4,
    skill_stamina=2,
    attack=0,
    move_cost=2,
    height=0,
    class_tag=RodentClassTag.SPECIALIST,
    entity_tags=[EntityTag.NO_ATTACK],
    skills=[
        EntitySkill(
            name="Rocket Boost",
            method_name="rocket_boost",
            reach=1,
            altitude=5,
            crumb_cost=2,
            tags=[],
        ),
    ],
)
class Mayo(Rodent):
    ROCKET_BOOST_HEIGHT_LIMIT = 5
    DODGE_CHANCE = 0.2
    DODGE_MIN_DISTANCE = 5

    def teleport(
        self, game_manager: "GameManager", coords: list[OddRCoord]
    ) -> SkillResult:
        assert len(coords) == 1
        game_manager.move_entity_uncheck(
            self, coords[0], custom_jump_height=self.ROCKET_BOOST_HEIGHT_LIMIT
        )
        return SkillCompleted.SUCCESS

    @entity_skill_check
    def rocket_boost(self, game_manager: "GameManager") -> SkillTargeting:
        return (
            SelectTarget(self, skill_index=0)
            .can_select_tile_without_collision()
            .add_custom_action(self.teleport)
            .to_skill_targeting(game_manager)
        )

    def on_damage_taken(
        self,
        game_manager: "GameManager",
        damage: int | InstantKill,
        source: SourceOfDamageOrHeal,
    ) -> int | None:
        if not isinstance(source, Entity):
            return None
        if source.pos.get_distance(self.pos) < self.DODGE_MIN_DISTANCE:
            return None
        if random.random() < self.DODGE_CHANCE:
            return 0
        return None

    def passive_descriptions(self) -> list[tuple[str, str]]:
        return [
            (
                "Escape Manuever",
                f"{self.DODGE_CHANCE:%} to dodge an attack from enemy at least {self.DODGE_MIN_DISTANCE} tiles away.",
            )
        ]

    def skill_descriptions(self) -> list[str]:
        return [
            f"Move 1 tile in any direction. Can go up to {self.ROCKET_BOOST_HEIGHT_LIMIT} height unit.",
        ]


@effect_data(EffectClearSide.ENEMY, name="The One's Brace")
class TheOneBrace(EntityEffect):
    def on_applied(self, game_manager: "GameManager", *, is_overriding: bool) -> None:
        assert isinstance(self.entity, TheOne)
        self.entity.defense += 5

    def on_turn_change(self, game_manager: "GameManager") -> None:
        pass

    def on_cleared(self, game_manager: "GameManager", *, is_overridden: bool) -> None:
        self.entity.defense -= 5

    def effect_descriptions(self) -> str:
        return "Brace for impact"


@rodent_data(
    name="The One",
    description="The strongest rodent in history. A one who has never known fear.",
    health=30,
    defense=2,
    speed=10,
    move_stamina=1,
    skill_stamina=3,
    attack=3,
    move_cost=15,
    height=2,
    class_tag=RodentClassTag.SPECIALIST,
    entity_tags=[],
    skills=[
        EntitySkill(
            name="The Punch",
            method_name="the_punch",
            reach=1,
            altitude=99,
            crumb_cost=20,
            tags=[],
        ),
        EntitySkill(
            name="Brace",
            method_name="brace",
            reach=None,
            altitude=None,
            crumb_cost=5,
            tags=[],
        ),
    ],
)
class TheOne(Rodent):
    PASSIVE_DISTANCE = 3
    PASSIVE_DEFENSE = 2

    @entity_skill_check
    def the_punch(self, game_manager: "GameManager") -> SkillTargeting:
        return (
            SelectTarget(self, skill_index=0)
            .can_select_enemy()
            .add_target_action(
                TargetAction(self).acquire_enemy_entity().damage(self.attack * 6)
            )
            .to_skill_targeting(game_manager)
        )

    @entity_skill_check
    def brace(self, game_manager: "GameManager") -> SkillCompleted:
        if TheOneBrace.name in self.effects:
            return SkillCompleted.CANCELLED
        game_manager.apply_effect(TheOneBrace(self, duration=1))
        return SkillCompleted.SUCCESS

    def on_heal(
        self, game_manager: "GameManager", heal: int, source: SourceOfDamageOrHeal
    ) -> int | None:
        return 0

    def on_ally_move(
        self,
        game_manager: "GameManager",
        ally: "Entity",
        path: list[OddRCoord],
        origin: OddRCoord,
    ) -> None:
        if (
            origin.get_distance(self.pos) <= self.PASSIVE_DISTANCE
            and path[-1].get_distance(self.pos) > self.PASSIVE_DISTANCE
        ):
            ally.defense -= self.PASSIVE_DEFENSE
        elif (
            origin.get_distance(self.pos) > self.PASSIVE_DISTANCE
            and path[-1].get_distance(self.pos) <= self.PASSIVE_DISTANCE
        ):
            ally.defense += self.PASSIVE_DEFENSE

    def passive_descriptions(self) -> list[tuple[str, str]]:
        return [
            (
                "Hope and Dream",
                f"All allies within {self.PASSIVE_DISTANCE}-tiles radius gain +{self.PASSIVE_DEFENSE} defense",
            ),
            (
                "Lonely",
                "Cannot regain HP through any mean and only 1 The One can be on the field at any given time.",
            ),
        ]

    def skill_descriptions(self) -> list[str]:
        return [
            f"The mission is to destroy the enemy. There's no cover that can stop this rodent. Deal {self.attack*6}(ATK*6) damage.",
            "Gain +5 defense for 1 of the enemy's turn.",
        ]
