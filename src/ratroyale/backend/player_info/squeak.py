from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from dataclasses import dataclass

from ..hexagon import OddRCoord

if TYPE_CHECKING:
    from ..game_manager import GameManager


@dataclass(frozen=True, kw_only=True)
class Squeak(ABC):
    crumb_cost: int
    is_deployment_zone_only: bool = True

    @abstractmethod
    def on_place(self, game_manager: "GameManager", coord: OddRCoord) -> bool:
        ...
