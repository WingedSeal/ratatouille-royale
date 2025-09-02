from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import TYPE_CHECKING, Protocol
from dataclasses import dataclass

from ..features.commmon import DeploymentZone


from ..hexagon import OddRCoord

if TYPE_CHECKING:
    from ..game_manager import GameManager
    from ..entities.rodent import Rodent


class SqueakType(Enum):
    RODENT = auto()
    TRICK = auto()


class SqueakOnPlace(Protocol):
    def __call__(self, game_manager: "GameManager", coord: OddRCoord) -> bool:
        ...


@dataclass(frozen=True, kw_only=True)
class Squeak(ABC):
    crumb_cost: int
    squeak_type: SqueakType
    is_deployment_zone_only: bool = True
    on_place: SqueakOnPlace


def summon_on_place(rodent_type: type["Rodent"]) -> SqueakOnPlace:
    def on_place(game_manager: "GameManager", coord: OddRCoord) -> bool:
        return summon(game_manager, coord, rodent_type)
    return on_place


def summon(game_manager: "GameManager", coord: OddRCoord, rodent_type: type["Rodent"]) -> bool:
    tile = game_manager.board.get_tile(coord)
    if tile is None:
        raise ValueError("Trying to summon rodent on None tile")
    if any(entity.collision for entity in tile.entities):
        return False
    if any(isinstance(feature, DeploymentZone) and feature.side == game_manager.turn for feature in tile.features):
        game_manager.board.add_entity(rodent_type(coord, game_manager.turn))
        return True
    return False
