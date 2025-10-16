import random
from typing import TYPE_CHECKING

from ...damage_heal_source import DamageHealSource
from ...tags import RodentClassTag
from ...entity import Entity, EntitySkill, SkillTargeting, entity_skill_check
from ..rodent import Rodent, rodent_data
from .common_skills import move

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

    @entity_skill_check
    def rocket_boost(self, game_manager: "GameManager") -> SkillTargeting:
        return SkillTargeting(
            1,
            self,
            self.skills[0],
            [
                neighbor
                for neighbor in self.pos.get_neighbors()
                if (tile := game_manager.board.get_tile(neighbor)) is not None
                and tile.is_collision(True)
            ],
            move(self, custom_jump_height=self.ROCKET_BOOST_HEIGHT_LIMIT),
            can_cancel=True,
        )

    def on_damage_taken(
        self, game_manager: "GameManager", damage: int, source: DamageHealSource
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
