from typing import TYPE_CHECKING


from ..entity_effect import EffectClearSide, RodentEffect, effect_data

if TYPE_CHECKING:
    from ..game_manager import GameManager


@effect_data(EffectClearSide.ALLY, name="Slowed")
class Slowed(RodentEffect):
    def on_turn_change(self, game_manager: "GameManager") -> None:
        pass

    def on_applied(self, game_manager: "GameManager", *, is_overriding: bool) -> None:
        self.rodent.speed -= int(self.intensity)

    def on_cleared(self, game_manager: "GameManager", *, is_overridden: bool) -> None:
        self.rodent.speed += int(self.intensity)

    def effect_descriptions(self) -> str:
        return "TODO"


@effect_data(EffectClearSide.ALLY, name="Stunned")
class Stunned(RodentEffect):
    def on_turn_change(self, game_manager: "GameManager") -> None:
        pass

    def on_applied(self, game_manager: "GameManager", *, is_overriding: bool) -> None:
        if self.rodent.max_skill_stamina is not None:
            self.rodent.max_skill_stamina *= -1
        if self.rodent.max_move_stamina is not None:
            self.rodent.max_move_stamina *= -1

    def on_cleared(self, game_manager: "GameManager", *, is_overridden: bool) -> None:
        if self.rodent.max_skill_stamina is not None:
            self.rodent.max_skill_stamina *= -1
        if self.rodent.max_move_stamina is not None:
            self.rodent.max_move_stamina *= -1

    def effect_descriptions(self) -> str:
        return "TODO"


@effect_data(EffectClearSide.ALLY, name="Poisoned")
class Poisoned(RodentEffect):
    def on_turn_change(self, game_manager: "GameManager") -> None:
        if game_manager.turn == self.rodent.side:
            game_manager.board.damage_entity(self.rodent, int(self.intensity))

    def on_applied(self, game_manager: "GameManager", *, is_overriding: bool) -> None:
        _ = game_manager
        _ = is_overriding

    def on_cleared(self, game_manager: "GameManager", *, is_overridden: bool) -> None:
        _ = game_manager
        _ = is_overridden

    def effect_descriptions(self) -> str:
        return "TODO"


@effect_data(EffectClearSide.ALLY, name="Bleeding")
class Bleeding(RodentEffect):
    def on_turn_change(self, game_manager: "GameManager") -> None:
        game_manager.board.damage_entity(self.rodent, int(self.intensity))

    def on_applied(self, game_manager: "GameManager", *, is_overriding: bool) -> None:
        if not is_overriding:
            game_manager.board.damage_entity(self.rodent, int(self.intensity))

    def on_cleared(self, game_manager: "GameManager", *, is_overridden: bool) -> None:
        _ = game_manager
        _ = is_overridden

    def effect_descriptions(self) -> str:
        return "TODO"
