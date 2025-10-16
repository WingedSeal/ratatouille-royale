from typing import TYPE_CHECKING

from ...instant_kill import INSTANT_KILL
from ...effects.global_rodent_effects import Stunned
from ...entity import EntitySkill, SkillCompleted, SkillTargeting, entity_skill_check
from ...tags import RodentClassTag, SkillTag
from ...timer import Timer, TimerClearSide
from ..rodent import Rodent, rodent_data
from .common_skills import (
    aoe_damage,
    apply_effect,
    apply_timer,
    normal_damage,
    select_targetable,
)

if TYPE_CHECKING:
    from ...game_manager import GameManager


@rodent_data(
    name="Ratbert Brewbelly",
    description="A bloated, beer-stained brown rat with bloodshot eyes and a sloshing belly who waddles unsteadily through combat. Armed with projectile vomit attacks that stun enemies with some damages.",
    health=7,
    defense=1,
    speed=3,
    move_stamina=2,
    skill_stamina=1,
    attack=3,
    move_cost=8,
    height=0,
    class_tag=RodentClassTag.DUELIST,
    entity_tags=[],
    skills=[
        EntitySkill(
            name="Projectile Vomit",
            method_name="projectile_vomit",
            reach=6,
            altitude=0,
            crumb_cost=10,
            tags=[],
        ),
    ],
)
class RatbertBrewbelly(Rodent):
    def vomit_timer_callback(self, timer: Timer, game_manager: "GameManager") -> None:
        game_manager.damage_entity(timer.entity, self.attack // 2, self)

    @entity_skill_check
    def projectile_vomit(self, game_manager: "GameManager") -> SkillTargeting:
        return select_targetable(
            game_manager.board,
            self,
            self.skills[0],
            [
                normal_damage(self.attack + 3, self),
                apply_effect(Stunned, duration=2, intensity=0),
                apply_timer(
                    TimerClearSide.ENEMY,
                    on_timer_over=self.vomit_timer_callback,
                    duration=2,
                ),
            ],
        )

    def skill_descriptions(self) -> list[str]:
        return [
            f"Launches chunky bile that 'stuns' enemies on impact for 2 turns, dealing {self.attack+3}(ATK+3) on the first turn and {self.attack//2}(ATK/2) on the second turn."
        ]


@rodent_data(
    name="Soda Kabooma",
    description="No idea what it is doing here, but it was told to hold this soda can, and hold the soda can it will.",
    health=9,
    defense=5,
    speed=2,
    move_stamina=2,
    skill_stamina=1,
    attack=5,
    move_cost=2,
    height=0,
    class_tag=RodentClassTag.DUELIST,
    entity_tags=[],
    skills=[
        EntitySkill(
            name="Shake the Can",
            method_name="shake_the_can",
            reach=0,
            altitude=0,
            crumb_cost=5,
            tags=[SkillTag.SELF_DEFEATED],
        ),
    ],
)
class SodaKabooma(Rodent):
    SHAKE_THE_CAN_RADIUS = 2

    @entity_skill_check
    def shake_the_can(self, game_manager: "GameManager") -> SkillCompleted:
        aoe_damage(
            self.attack * 2 + 1, self.SHAKE_THE_CAN_RADIUS, self, is_friendly_fire=True
        )(game_manager, [self.pos])
        game_manager.damage_entity(self, INSTANT_KILL, self)
        return SkillCompleted.SUCCESS

    def skill_descriptions(self) -> list[str]:
        return [
            f"Shakes the soda can to make it explode, dealing {self.attack * 2 + 1}(ATK*2+1) damage to all rodents (including its allies) in a {self.SHAKE_THE_CAN_RADIUS}-tile radius. This rodent is then defeated afterwards."
        ]


@rodent_data(
    name="Pea Pea Pool Pool",
    description="A rodent in a pool with a gun. That is if a cup of water can be called pool and a pea can be called a gun.",
    health=10,
    defense=2,
    speed=10,
    move_stamina=2,
    skill_stamina=3,
    attack=4,
    move_cost=3,
    height=0,
    class_tag=RodentClassTag.DUELIST,
    entity_tags=[],
    skills=[
        EntitySkill(
            name="Pea",
            method_name="pea",
            reach=12,
            altitude=1,
            crumb_cost=5,
            tags=[],
        ),
    ],
)
class PeaPeaPoolPool(Rodent):

    @entity_skill_check
    def pea(self, game_manager: "GameManager") -> SkillTargeting:
        return select_targetable(
            game_manager.board, self, self.skills[0], normal_damage(self.attack, self)
        )

    def skill_descriptions(self) -> list[str]:
        return [
            f"Shoot the pea inside the pod at an enemy dealing {self.attack}(ATK) damage."
        ]
