# dummy_backend.py
from dataclasses import dataclass
from ratroyale.visual.sprite_registry import SpriteRegistryKey


@dataclass
class DummyCoord:
    q: int
    r: int


@dataclass
class DummyTile:
    coord: DummyCoord
    sprite_variant: SpriteRegistryKey = SpriteRegistryKey.DEFAULT_TILE


@dataclass
class DummyPos:
    x: int
    y: int


@dataclass
class DummyEntity:
    pos: DummyPos
    sprite_variant: SpriteRegistryKey = SpriteRegistryKey.DEFAULT_ENTITY
