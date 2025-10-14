from typing import TYPE_CHECKING

from ..entities.rodent import Rodent
from ..entity_effect import EffectClearSide, EntityEffect, effect_data

if TYPE_CHECKING:
    from ..game_manager import GameManager


@effect_data(EffectClearSide.ALLY, name="Slowed")
class Slowed(EntityEffect):
    def on_turn_change(self, game_manager: "GameManager") -> None:
        pass

    def on_applied(self, game_manager: "GameManager", *, is_overriding: bool) -> None:
        if isinstance(self.entity, Rodent):
            self.entity.speed -= int(self.intensity)

    def on_cleared(self, game_manager: "GameManager", *, is_overridden: bool) -> None:
        if isinstance(self.entity, Rodent):
            self.entity.speed += int(self.intensity)

    def effect_descriptions(self) -> str:
        return "TODO"


@effect_data(EffectClearSide.ALLY, name="Stunned")
class Stunned(EntityEffect):
    def on_turn_change(self, game_manager: "GameManager") -> None:
        pass

    def on_applied(self, game_manager: "GameManager", *, is_overriding: bool) -> None:
        if self.entity.max_skill_stamina is not None:
            self.entity.max_skill_stamina *= -1
        if isinstance(self.entity, Rodent):
            if self.entity.max_move_stamina is not None:
                self.entity.max_move_stamina *= -1

    def on_cleared(self, game_manager: "GameManager", *, is_overridden: bool) -> None:
        if self.entity.max_skill_stamina is not None:
            self.entity.max_skill_stamina *= -1
        if isinstance(self.entity, Rodent):
            if self.entity.max_move_stamina is not None:
                self.entity.max_move_stamina *= -1

    def effect_descriptions(self) -> str:
        return "TODO"


@effect_data(EffectClearSide.ALLY, name="Poisoned")
class Poisoned(EntityEffect):
    def on_turn_change(self, game_manager: "GameManager") -> None:
        if game_manager.turn == self.entity.side:
            game_manager.board.damage_entity(self.entity, int(self.intensity))

    def on_applied(self, game_manager: "GameManager", *, is_overriding: bool) -> None:
        _ = game_manager
        _ = is_overriding

    def on_cleared(self, game_manager: "GameManager", *, is_overridden: bool) -> None:
        _ = game_manager
        _ = is_overridden

    def effect_descriptions(self) -> str:
        return "TODO"


@effect_data(EffectClearSide.ALLY, name="Bleeding")
class Bleeding(EntityEffect):
    def on_turn_change(self, game_manager: "GameManager") -> None:
        game_manager.board.damage_entity(self.entity, int(self.intensity))

    def on_applied(self, game_manager: "GameManager", *, is_overriding: bool) -> None:
        if not is_overriding:
            game_manager.board.damage_entity(self.entity, int(self.intensity))

    def on_cleared(self, game_manager: "GameManager", *, is_overridden: bool) -> None:
        _ = game_manager
        _ = is_overridden

    def effect_descriptions(self) -> str:
        return "TODO"
