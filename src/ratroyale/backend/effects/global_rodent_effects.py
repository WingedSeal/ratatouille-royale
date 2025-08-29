
from typing import TYPE_CHECKING

from ..side import Side
from ..entities.rodent import Rodent
from ..error import RodentEffectNotOnRodentError
from ..entity_effect import EffectClearSide, EntityEffect, effect_data
if TYPE_CHECKING:
    from ..entity import Entity


@effect_data(EffectClearSide.ALLY, name="Slowness")
class Slowness(EntityEffect):
    rodent: Rodent

    def __init__(self, entity: "Entity", *, duration: int | None, intensity: int) -> None:
        self.intensity = intensity
        if not isinstance(entity, Rodent):
            raise RodentEffectNotOnRodentError()
        self.rodent = entity
        super().__init__(entity, duration=duration, intensity=intensity)

    def on_turn_change(self, turn_count_before_change: int, turn_before_change: Side):
        pass

    def on_applied(self, *, is_overriding: bool):
        self.rodent.speed -= self.intensity

    def on_cleared(self, *, is_overriden: bool):
        self.rodent.speed += self.intensity
