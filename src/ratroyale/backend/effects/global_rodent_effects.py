from ..side import Side
from ..entity_effect import EffectClearSide, effect_data, RodentEffect


@effect_data(EffectClearSide.ALLY, name="Slowness")
class Slowness(RodentEffect):
    def on_turn_change(self, turn_count_before_change: int, turn_before_change: Side):
        _ = turn_count_before_change
        _ = turn_before_change
        pass

    def on_applied(self, *, is_overriding: bool):
        _ = is_overriding
        self.rodent.speed -= self.intensity

    def on_cleared(self, *, is_overriden: bool):
        _ = is_overriden
        self.rodent.speed += self.intensity
