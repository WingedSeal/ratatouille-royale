from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Iterable, Protocol

from ..hexagon import OddRCoord

if TYPE_CHECKING:
    from ..entities.rodent import Rodent
    from ..game_manager import GameManager
    from ..entity import Entity


@dataclass(frozen=True)
class SqueakInfo:
    @staticmethod
    @abstractmethod
    def is_rodent() -> bool: ...

    @staticmethod
    @abstractmethod
    def is_trick() -> bool: ...


@dataclass(frozen=True)
class RodentSqueakInfo(SqueakInfo):
    rodent: type["Rodent"]

    @staticmethod
    def is_rodent() -> bool:
        return True

    @staticmethod
    def is_trick() -> bool:
        return False


@dataclass(frozen=True)
class TrickSqueakInfo(SqueakInfo):
    description: str
    related_entities: list[type["Entity"]]

    @staticmethod
    def is_rodent() -> bool:
        return True

    @staticmethod
    def is_trick() -> bool:
        return False


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
    squeak_info: SqueakInfo
    on_place: SqueakOnPlace
    get_placable_tiles: SqueakGetPlacableTiles
    trick_description: str | None = None
    SQEAK_MAP: ClassVar[dict[str, "Squeak"]] = {}

    def __post_init__(self) -> None:
        type(self).SQEAK_MAP[self.name] = self


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


def summon_on_place(entity_type: type["Entity"]) -> SqueakOnPlace:
    def on_place(game_manager: "GameManager", coord: OddRCoord) -> None:
        summon(game_manager, coord, entity_type)

    return on_place


def summon(
    game_manager: "GameManager", coord: OddRCoord, entity_type: type["Entity"]
) -> "Entity":
    tile = game_manager.board.get_tile(coord)
    if tile is None:
        raise ValueError("Trying to summon rodent on None tile")
    entity = entity_type(coord, game_manager.turn)
    game_manager.board.add_entity(entity, game_manager)
    return entity
