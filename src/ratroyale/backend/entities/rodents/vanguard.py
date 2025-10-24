from typing import TYPE_CHECKING

from ratroyale.backend.entities.rodents.common_skills import SelectTarget, TargetAction

from ...entity import EntitySkill, SkillTargeting, entity_skill_check
from ...tags import RodentClassTag
from ..rodent import Rodent, rodent_data

if TYPE_CHECKING:
    from ...game_manager import GameManager


@rodent_data(
    name="TailBlazer",
    description="The rodent that will never deny a call for adventures.",
    health=8,
    defense=2,
    speed=8,
    move_stamina=2,
    skill_stamina=3,
    attack=3,
    move_cost=3,
    height=0,
    class_tag=RodentClassTag.VANGUARD,
    entity_tags=[],
    skills=[
        EntitySkill(
            name="Stab", method_name="stab", reach=2, altitude=0, crumb_cost=3, tags=[]
        ),
        EntitySkill(
            name="Spear Launching",
            method_name="spear_launching",
            reach=5,
            altitude=0,
            crumb_cost=7,
            tags=[],
        ),
    ],
)
class TailBlazer(Rodent):
    @entity_skill_check
    def stab(self, game_manager: "GameManager") -> SkillTargeting:
        return (
            SelectTarget(self, skill_index=0)
            .can_select_enemy()
            .add_target_action(
                TargetAction(self).acquire_enemy().damage(self.attack + 1)
            )
            .to_skill_targeting(game_manager)
        )

    @entity_skill_check
    def spear_launching(self, game_manager: "GameManager") -> SkillTargeting:
        return (
            SelectTarget(self, skill_index=1)
            .can_select_enemy()
            .add_target_action(TargetAction(self).acquire_enemy().damage(self.attack))
            .to_skill_targeting(game_manager)
        )

    def skill_descriptions(self) -> list[str]:
        return [
            f"Stab an enemy with a toothpick dealing {self.attack + 1}(ATK+1) damage.",
            f"Throw a toothpick at an enemy dealing {self.attack}(ATK) damage.",
        ]
