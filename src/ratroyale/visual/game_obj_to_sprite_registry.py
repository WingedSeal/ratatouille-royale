from enum import Enum, auto
from typing import Type
from ratroyale.backend.entities.rodents.vanguard import TailBlazer
from ratroyale.backend.entity import Entity
from ratroyale.backend.tile import Tile

# TODO: refactor entity/tile sprite drawing into type-based handlers.

class SpriteRegistryKey(Enum):
  DEFAULT_TILE = auto()
  DEFAULT_ENTITY = auto()
  RODENT_TAILBLAZER = auto()

TILE_TO_SPRITE_REGISTRY: dict[Type[Tile], SpriteRegistryKey] = {
}

ENTITY_TO_SPRITE_REGISTRY: dict[Type[Entity], SpriteRegistryKey] = {
    TailBlazer: SpriteRegistryKey.RODENT_TAILBLAZER
}