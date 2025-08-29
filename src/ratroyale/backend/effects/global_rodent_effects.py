from ..side import Side
from ..entity_effect import EffectClearSide, effect_data, RodentEffect


@effect_data(EffectClearSide.ALLY, name="Slowness")
class Slowness(RodentEffect):
    def on_turn_change(self, turn_count_before_change: int, turn_before_change: Side):
        pass

    def on_applied(self, *, is_overriding: bool):
        self.rodent.speed -= self.intensity

    def on_cleared(self, *, is_overriden: bool):
        self.rodent.speed += self.intensity
