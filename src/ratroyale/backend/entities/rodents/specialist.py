import random
from typing import TYPE_CHECKING

from ratroyale.backend.entities.rodents.common_skills import SelectTarget
from ratroyale.backend.hexagon import OddRCoord

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
from ...tags import RodentClassTag
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
    entity_tags=[],
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
