from typing import TYPE_CHECKING

from ...instant_kill import INSTANT_KILL
from ...timer import Timer, TimerClearSide
from ...entity import Entity, entity_data

if TYPE_CHECKING:
    from ...game_manager import GameManager


@entity_data(
    name="Sundial",
    description="The ultimate last resort. The sign of true desperation. \
If not destroyed within 5 of enemy's turn, explode and set every of your lair's health to 1 \
and kill every entity in the field. (Cannot work if every lair's health is already 1)",
    health=5,
    defense=0,
    collision=True,
)
class Sundial(Entity):
    timer: Timer | None = None

    def on_summon(self, game_manager: "GameManager") -> None:
        self.timer = Timer(
            self,
            TimerClearSide.ENEMY,
            duration=5,
            on_turn_change=None,
            on_timer_over=self.explode,
        )

        game_manager.apply_timer(self.timer)

    def explode(self, timer: Timer, game_manager: "GameManager") -> None:
        assert self.side is not None
        for lair in game_manager.board.cache.lairs[self.side]:
            lair.health = 1

        for entity in game_manager.board.cache.entities_with_hp:
            if entity.health is not None:
                game_manager.damage_entity(entity, INSTANT_KILL, self)

    def passive_descriptions(self) -> list[tuple[str, str]]:
        return [
            (
                "Explosion",
                f"Explode in {self.timer.duration if self.timer is not None else 5} of enemy's turn killing every entity in the field and set every of your lair's health to 1",
            )
        ]
