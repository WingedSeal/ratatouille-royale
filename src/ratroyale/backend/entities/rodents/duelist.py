from typing import TYPE_CHECKING

from ratroyale.backend.entities.rodents.common_skills import SelectTarget, TargetAction

from ...source_of_damage_or_heal import SourceOfDamageOrHeal
from ...instant_kill import INSTANT_KILL, InstantKill
from ...effects.global_rodent_effects import Stunned
from ...entity import EntitySkill, SkillCompleted, SkillTargeting, entity_skill_check
from ...tags import RodentClassTag, SkillTag
from ...timer import Timer, TimerClearSide
from ..rodent import Rodent, rodent_data

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
        return (
            SelectTarget(self, skill_index=0)
            .can_select_enemy()
            .add_target_action(
                TargetAction(self)
                .acquire_enemy()
                .damage(self.attack + 3)
                .apply_effect(Stunned, duration=2)
                .apply_timer(
                    TimerClearSide.ENEMY,
                    on_timer_over=self.vomit_timer_callback,
                    duration=2,
                )
            )
            .to_skill_targeting(game_manager)
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
            tags=[SkillTag.SELF_DEFEATED, SkillTag.AOE],
        ),
    ],
)
class SodaKabooma(Rodent):
    SHAKE_THE_CAN_RADIUS = 2

    @entity_skill_check
    def shake_the_can(self, game_manager: "GameManager") -> SkillCompleted:
        TargetAction(self).aoe(self.SHAKE_THE_CAN_RADIUS).acquire_any().damage(
            self.attack * 2 + 1
        ).build_skill_callback()(game_manager, [self.pos])
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
        return (
            SelectTarget(self, skill_index=0)
            .can_select_enemy()
            .add_target_action(
                TargetAction(self)
                .acquire_enemy()
                .damage(self.attack // 2)
                .damage(self.attack // 2)
            )
            .to_skill_targeting(game_manager)
        )

    def skill_descriptions(self) -> list[str]:
        return [
            f"Shoot the peas inside the pod at an enemy dealing {self.attack}(ATK/2) damage twice."
        ]


@rodent_data(
    name="Mortar",
    description="A coward with an access to artillery strike.",
    health=12,
    defense=3,
    speed=3,
    move_stamina=2,
    skill_stamina=2,
    attack=5,
    move_cost=2,
    height=0,
    class_tag=RodentClassTag.DUELIST,
    entity_tags=[],
    skills=[
        EntitySkill(
            name="Artillery Strike",
            method_name="artillery_strike",
            reach=7,
            altitude=3,
            crumb_cost=10,
            tags=[SkillTag.AOE],
        ),
        EntitySkill(
            name="Artillery Strikes",
            method_name="artillery_strikes",
            reach=7,
            altitude=3,
            crumb_cost=30,
            tags=[SkillTag.AOE],
        ),
    ],
)
class Mortar(Rodent):
    double_speed_timer: Timer | None

    @entity_skill_check
    def artillery_strike(self, game_manager: "GameManager") -> SkillTargeting:
        return (
            SelectTarget(self, skill_index=0)
            .can_select_any_tile()
            .add_target_action(TargetAction(self).aoe(2).damage(self.attack + 4))
            .to_skill_targeting(game_manager)
        )

    @entity_skill_check
    def artillery_strikes(self, game_manager: "GameManager") -> SkillTargeting:
        return (
            SelectTarget(self, skill_index=1)
            .can_select_any_tile()
            .add_target_action(TargetAction(self).aoe(3).damage(self.attack + 8))
            .to_skill_targeting(game_manager)
        )

    def skill_descriptions(self) -> list[str]:
        return [
            f"Launch the artillery at any tile damaging all enemy within 2-tiles radius dealing {self.attack + 4}(ATK+4) damage.",
            f"Launch multiple artilleries at any tile damaging all enemy within 3-tiles radius dealing {self.attack + 8}(ATK+8) damage.",
        ]

    def __clear_double_speed(self, timer: "Timer", game_manager: "GameManager") -> None:
        self.speed -= type(self).speed
        self.double_speed_timer = None

    def passive_descriptions(self) -> list[tuple[str, str]]:
        return [("A Coward", "After taking damage, gain 100% speed for 1 turn.")]

    def on_damage_taken(
        self,
        game_manager: "GameManager",
        damage: int | InstantKill,
        source: SourceOfDamageOrHeal,
    ) -> int | None:
        if self.double_speed_timer is not None:
            return None
        self.speed += type(self).speed
        self.double_speed_timer = Timer(
            self,
            TimerClearSide.ALLY,
            on_timer_over=self.__clear_double_speed,
            on_turn_change=None,
            duration=1,
        )
        game_manager.apply_timer(self.double_speed_timer)
        return None
