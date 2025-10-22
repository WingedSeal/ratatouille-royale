from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, ClassVar, Iterable, Protocol

from ..hexagon import OddRCoord

if TYPE_CHECKING:
    from ..entities.rodent import Rodent
    from ..game_manager import GameManager
    from ..entity import Entity


class SqueakType(Enum):
    RODENT = auto()
    TRICK = auto()


class SqueakOnPlace(Protocol):
    def __call__(
        self, game_manager: "GameManager", coord: OddRCoord
    ) -> "Squeak | None": ...


class SqueakGetPlacableTiles(Protocol):
    def __call__(self, game_manager: "GameManager") -> Iterable[OddRCoord]: ...


@dataclass(frozen=True, kw_only=True)
class Squeak:
    name: str
    crumb_cost: int
    squeak_type: SqueakType
    on_place: SqueakOnPlace
    get_placable_tiles: SqueakGetPlacableTiles
    rodent: "type[Rodent] | None"
    SQEAK_MAP: ClassVar[dict[str, "Squeak"]] = {}
    REVERSED_SQEAK_MAP: ClassVar[dict["Squeak", str]] = {}

    def __post_init__(self) -> None:
        type(self).SQEAK_MAP[self.name] = self
        type(self).REVERSED_SQEAK_MAP[self] = self.name


def rodent_placable_tile(game_manager: "GameManager") -> Iterable[OddRCoord]:
    side = game_manager.turn
    used_coord: set[OddRCoord] = set()
    for deployment_zone in game_manager.board.cache.deployment_zones[side]:
        for pos in deployment_zone.shape:
            if pos in used_coord:
                continue
            used_coord.add(pos)
            tile = game_manager.board.get_tile(pos)
            if tile is None:
                continue
            if tile.is_collision(True):
                continue
            yield pos


def summon_on_place(rodent_type: type["Rodent"]) -> SqueakOnPlace:
    def on_place(game_manager: "GameManager", coord: OddRCoord) -> None:
        summon(game_manager, coord, rodent_type)

    return on_place


def summon(
    game_manager: "GameManager", coord: OddRCoord, rodent_type: type["Rodent"]
) -> "Entity":
    tile = game_manager.board.get_tile(coord)
    if tile is None:
        raise ValueError("Trying to summon rodent on None tile")
    entity = rodent_type(coord, game_manager.turn)
    game_manager.board.add_entity(entity, game_manager)
    return entity
