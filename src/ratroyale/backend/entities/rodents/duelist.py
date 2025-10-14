from typing import TYPE_CHECKING

from ...timer import Timer, TimerClearSide
from ...effects.global_rodent_effects import Stunned
from ...tags import RodentClassTag
from ...entity import EntitySkill, SkillTargeting, entity_skill_check
from ..rodent import Rodent, rodent_data
from .common_skills import apply_effect, apply_timer, normal_damage, select_targetable

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
        game_manager.damage_entity(timer.entity, self.attack // 2)

    @entity_skill_check
    def projectile_vomit(self, game_manager: "GameManager") -> SkillTargeting:
        return select_targetable(
            game_manager.board,
            self,
            self.skills[0],
            [
                normal_damage(self.attack + 3),
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
