from typing import TYPE_CHECKING

from ...effects.global_rodent_effects import Stunned
from ...entity_effect import EffectClearSide, RodentEffect, effect_data
from ...tags import RodentClassTag
from ...entity import EntitySkill, SkillTargeting, entity_skill_check
from ..rodent import Rodent, rodent_data
from .common_skills import apply_effect, normal_damage, select_targetable

if TYPE_CHECKING:
    from ...game_manager import GameManager


@effect_data(EffectClearSide.ENEMY, name="RatbertBrewbellyVomit")
class RatbertBrewbellyVomit(RodentEffect):
    def on_applied(self, game_manager: "GameManager", *, is_overriding: bool) -> None:
        pass

    def on_turn_change(self, game_manager: "GameManager") -> None:
        pass

    def on_cleared(self, game_manager: "GameManager", *, is_overridden: bool) -> None:
        if is_overridden:
            return
        game_manager.board.damage_entity(self.rodent, int(self.intensity))

    def effect_descriptions(self) -> str:
        return "TODO"


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
    @entity_skill_check
    def projectile_vomit(self, game_manager: "GameManager") -> SkillTargeting:
        return select_targetable(
            game_manager.board,
            self,
            self.skills[0],
            [
                normal_damage(self.attack + 3),
                apply_effect(Stunned, duration=2, intensity=0),
                apply_effect(
                    RatbertBrewbellyVomit,
                    duration=2,
                    intensity=self.attack // 2,
                    stack_intensity=True,
                ),
            ],
        )

    def skill_descriptions(self) -> list[str]:
        return [
            f"Launches chunky bile that 'stuns' enemies on impact for 2 turns, dealing {self.attack+3}(ATK+3) on the first turn and {self.attack//2}(ATK/2) on the second turn. If attacked multiple times, the second damage will be delayed and applied at once."
        ]
