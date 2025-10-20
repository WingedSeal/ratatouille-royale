from typing import TYPE_CHECKING

from ...entity import EntitySkill, SkillTargeting, entity_skill_check
from ...tags import RodentClassTag
from ..rodent import Rodent, rodent_data
from .common_skills import normal_damage, select_targetable

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
        return select_targetable(
            game_manager.board,
            self,
            self.skills[0],
            normal_damage(self.attack + 1, self),
        )

    @entity_skill_check
    def spear_launching(self, game_manager: "GameManager") -> SkillTargeting:
        return select_targetable(
            game_manager.board, self, self.skills[1], normal_damage(self.attack, self)
        )

    def skill_descriptions(self) -> list[str]:
        return [
            f"Stab an enemy with a toothpick dealing {self.attack + 1}(ATK+1) damage.",
            f"Throw a toothpick at an enemy dealing {self.attack}(ATK) damage.",
        ]
