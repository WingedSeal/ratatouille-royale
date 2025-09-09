from enum import Enum, auto
from typing import TYPE_CHECKING, Iterable, Protocol
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


class SqueakGetPlacableTiles(Protocol):
    def __call__(self, game_manager: "GameManager") -> Iterable[OddRCoord]:
        ...


@dataclass(frozen=True, kw_only=True)
class Squeak:
    crumb_cost: int
    squeak_type: SqueakType
    on_place: SqueakOnPlace
    get_placable_tiles: SqueakGetPlacableTiles


def rodent_placable_tile(game_manager: "GameManager") -> Iterable[OddRCoord]:
    side = game_manager.turn
    used_coord: set[OddRCoord] = set()
    for deployment_zone in game_manager.board.cache.deployment_zones[side]:
        for pos in deployment_zone.resolve_shape():
            if pos in used_coord:
                continue
            used_coord.add(pos)
            yield pos


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
