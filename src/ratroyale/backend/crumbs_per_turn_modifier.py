from collections import defaultdict
from dataclasses import dataclass, field
import math
from typing import Protocol

from .side import Side


class BaseCrumbsPerTurn(Protocol):
    def __call__(self, turn_count: int) -> int: ...


def default_base_crumbs_per_turn(turn_count: int) -> int:
    return min(math.ceil(turn_count / 4) * 10, 50)


@dataclass
class CrumbsPerTurnModifier:
    base_crumbs_per_turn: BaseCrumbsPerTurn
    multiplier: dict[Side, float] = field(default_factory=lambda: defaultdict(float))
    adder: dict[Side, int] = field(default_factory=lambda: defaultdict(int))
    turn_multiplier: list[tuple[range, float]] = field(default_factory=list)
    turn_adder: list[tuple[range, int]] = field(default_factory=list)

    def _get_turn_adder(self, turn_count: int) -> int:
        total_adder = 0
        for turn_range, adder in self.turn_adder:
            if turn_count in turn_range:
                total_adder += adder
        return total_adder

    def _get_turn_multiplier(self, turn_count: int) -> float:
        total_multiplier = 1.0
        for turn_range, multiplier in self.turn_multiplier:
            if turn_count in turn_range:
                total_multiplier += multiplier
        return total_multiplier

    def get_crumbs(self, turn_count: int, turn_side: Side) -> int:
        crumbs = self.base_crumbs_per_turn(turn_count)
        crumbs = math.floor(
            crumbs
            * (self._get_turn_multiplier(turn_count) + self.multiplier[turn_side])
        )
        crumbs += self._get_turn_adder(turn_count) + self.adder[turn_side]
        return crumbs
