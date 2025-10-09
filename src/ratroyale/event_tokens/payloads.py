from dataclasses import dataclass
from ratroyale.backend.tile import Tile
from ratroyale.backend.entity import Entity

#  from ratroyale.backend.card import Card or smth


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
class CardPayload(Payload):
    card: str  # Placeholder


@dataclass
class CardPlacementPayload(Payload):
    card: str
    tile: Tile
