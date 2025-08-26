# Card

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from dataclasses import dataclass

from ..hexagon import OddRCoord

if TYPE_CHECKING:
    from ..board import Board


@dataclass(frozen=True)
class Squeak(ABC):
    crumb_cost: int

    @abstractmethod
    def on_place(self, board: "Board", coord: OddRCoord) -> bool:
        ...
