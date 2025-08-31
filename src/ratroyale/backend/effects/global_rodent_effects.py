from typing import TYPE_CHECKING
from ..side import Side
from ..entity_effect import EffectClearSide, effect_data, RodentEffect

if TYPE_CHECKING:
    from ..game_manager import GameManager


@effect_data(EffectClearSide.ALLY, name="Slowed")
class Slowed(RodentEffect):
    def on_turn_change(self, game_manager: "GameManager") -> None:
        _ = game_manager

    def on_applied(self, game_manager: "GameManager", *, is_overriding: bool) -> None:
        _ = game_manager
        _ = is_overriding
        self.rodent.speed -= self.intensity

    def on_cleared(self, game_manager: "GameManager", *, is_overridden: bool) -> None:
        _ = game_manager
        _ = is_overridden
        self.rodent.speed += self.intensity


@effect_data(EffectClearSide.ALLY, name="Poisoned")
class Poisoned(RodentEffect):
    def on_turn_change(self, game_manager: "GameManager") -> None:
        if game_manager.turn == self.rodent.side:
            game_manager.board.damage_entity(self.rodent, self.intensity)

    def on_applied(self, game_manager: "GameManager", *, is_overriding: bool) -> None:
        _ = game_manager
        _ = is_overriding

    def on_cleared(self, game_manager: "GameManager", *, is_overridden: bool) -> None:
        _ = game_manager
        _ = is_overridden


@effect_data(EffectClearSide.ALLY, name="Bleeding")
class Bleeding(RodentEffect):
    def on_turn_change(self, game_manager: "GameManager") -> None:
        game_manager.board.damage_entity(self.rodent, self.intensity)

    def on_applied(self, game_manager: "GameManager", *, is_overriding: bool) -> None:
        if not is_overriding:
            game_manager.board.damage_entity(self.rodent, self.intensity)

    def on_cleared(self, game_manager: "GameManager", *, is_overridden: bool) -> None:
        _ = game_manager
        _ = is_overridden
