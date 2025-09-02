from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import TYPE_CHECKING
from dataclasses import dataclass


from ..hexagon import OddRCoord

if TYPE_CHECKING:
    from ..game_manager import GameManager
    from ..entities.rodent import Rodent


class SqueakType(Enum):
    RODENT = auto()
    TRICK = auto()


@dataclass(frozen=True, kw_only=True)
class Squeak(ABC):
    crumb_cost: int
    squeak_type: SqueakType
    is_deployment_zone_only: bool = True

    @abstractmethod
    def on_place(self, game_manager: "GameManager", coord: OddRCoord) -> bool:
        ...


def summon(game_manager: "GameManager", coord: OddRCoord, rodent_type: type["Rodent"]) -> bool:
    if game_manager.board.is_collision(coord):
        return False
    game_manager.board.add_entity(rodent_type(coord, game_manager.turn))
    return True
