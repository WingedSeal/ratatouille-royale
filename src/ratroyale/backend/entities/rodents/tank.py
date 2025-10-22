from typing import TYPE_CHECKING

from ratroyale.backend.entities.rodents.common_skills import SelectTarget, TargetAction

from ...entity import EntitySkill, SkillCompleted, SkillTargeting, entity_skill_check
from ...side import Side
from ...tags import RodentClassTag
from ..rodent import Rodent, rodent_data

if TYPE_CHECKING:
    from ...game_manager import GameManager


@rodent_data(
    name="Cracker",
    description="Reliable rodent using cracker as its shield. It'll defense its friends at any cost.",
    health=9,
    defense=5,
    speed=3,
    move_stamina=2,
    skill_stamina=3,
    attack=3,
    move_cost=2,
    height=2,
    class_tag=RodentClassTag.TANK,
    entity_tags=[],
    skills=[
        EntitySkill(
            name="Bread Slap",
            method_name="bread_slap",
            reach=1,
            altitude=0,
            crumb_cost=3,
            tags=[],
        ),
        EntitySkill(
            name="Abandon Bread",
            method_name="abandon_bread",
            reach=None,
            crumb_cost=1,
            altitude=None,
            tags=[],
        ),
    ],
)
class Cracker(Rodent):
    is_bread_abandoned = False

    @entity_skill_check
    def bread_slap(self, game_manager: "GameManager") -> SkillTargeting:
        return (
            SelectTarget(self, skill_index=0)
            .can_select_enemy()
            .add_target_action(TargetAction(self).acquire_enemy().damage(self.attack))
            .to_skill_targeting(game_manager)
        )

    @entity_skill_check
    def abandon_bread(self, game_manager: "GameManager") -> SkillCompleted:
        if self.is_bread_abandoned:
            return SkillCompleted.CANCELLED
        self.is_bread_abandoned = True
        self.height -= 1
        self.defense -= type(self).defense
        self.speed += 12
        return SkillCompleted.SUCCESS

    def on_turn_change(self, game_manager: "GameManager", turn_change_to: Side) -> None:
        if turn_change_to != self.side:
            return

        tile = game_manager.board.get_tile(self.pos)
        assert tile is not None
        for entity in tile.entities:
            if entity is self:
                continue
            if entity.side == self.side:
                game_manager.heal_entity(self, 1, self)
                return
        for neighbor in self.pos.get_reachable_coords(3):
            tile = game_manager.board.get_tile(neighbor)
            if tile is None:
                continue
            for entity in tile.entities:
                if entity.side == self.side:
                    game_manager.heal_entity(self, 1, self)
                    return

    def skill_descriptions(self) -> list[str]:
        return [
            f"Slap your enemy with bread dealing {self.attack}(ATK) damage.",
            "Throw away the cracker reducing defense to 0 and height to 1 until defeated. Increase speed by 12. Can only be used once per deployment.",
        ]

    def passive_descriptions(self) -> list[tuple[str, str]]:
        return [
            (
                "Bread Good",
                "Heal 1 HP per at the start of your turn when there is at least 1 ally within 3 tiles.",
            )
        ]
