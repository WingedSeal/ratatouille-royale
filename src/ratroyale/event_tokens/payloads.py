from dataclasses import dataclass
from ratroyale.backend.tile import Tile
from ratroyale.backend.entity import Entity
from ratroyale.backend.hexagon import OddRCoord
from ratroyale.backend.board import Board
from ratroyale.backend.player_info.squeak import Squeak
from typing import Iterable


@dataclass
class Payload:
    pass


@dataclass
class TilePayload(Payload):
    tile: Tile


@dataclass
class GameSetupPayload(Payload):
    board: Board
    hand_squeaks: list[Squeak]
    starting_crumbs: int


@dataclass
class CrumbUpdatePayload(Payload):
    new_crumb_amount: int


@dataclass
class SqueakDrawnPayload(Payload):
    squeak: Squeak


@dataclass
class EntityPayload(Payload):
    entity: Entity


@dataclass
class SqueakPayload(Payload):
    squeak: Squeak


@dataclass
class SqueakPlacableTilesPayload(Payload):
    coord_list: Iterable[OddRCoord]


@dataclass
class SqueakPlacementPayload(Payload):
    hand_index: int
    tile_coord: OddRCoord
