from dataclasses import dataclass

from ratroyale.backend.entity import Entity
from ratroyale.backend.tile import Tile


@dataclass
class Payload:
    pass


@dataclass
class TilePayload(Payload):
    tile: Tile


@dataclass
class EntityPayload(Payload):
    entity: Entity


@dataclass
class SqueakPayload(Payload):
    squeak_index: int


@dataclass
class SqueakPlacementPayload(Payload):
    squeak_index: int
    tile: Tile
