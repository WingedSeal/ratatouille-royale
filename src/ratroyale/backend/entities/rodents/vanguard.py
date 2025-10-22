from typing import TYPE_CHECKING

from ...side import Side
from .common_skills import SelectTarget, TargetAction
from ...entity import EntitySkill, SkillTargeting, entity_skill_check
from ...tags import RodentClassTag
from ..rodent import Rodent, rodent_data

if TYPE_CHECKING:
    from ...game_manager import GameManager
    from ...board import Board


@rodent_data(
    name="Tailblazer",
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
class Tailblazer(Rodent):
    on_speed: bool = False

    def on_spawn(self, board: "Board") -> None:
        if not any(
            isinstance(entity, Rodent) for entity in board.cache.sides[self.side]
        ):
            self.on_speed = True
            self.speed += 2

    def on_turn_change(self, game_manager: "GameManager", turn_change_to: Side) -> None:
        if self.on_speed and any(
            isinstance(entity, Rodent)
            for entity in game_manager.board.cache.sides[self.side]
        ):
            self.speed -= 2

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

    def passive_descriptions(self) -> list[tuple[str, str]]:
        return [
            (
                "Pioneer",
                "When placed, if there's no other ally rodents on the field, gain +2 speed until the turn after there's one.",
            )
        ]
