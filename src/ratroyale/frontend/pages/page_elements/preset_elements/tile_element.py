from ..element import ElementWrapper
from ..spatial_component import Camera
from ratroyale.backend.tile import Tile
from ratroyale.backend.hexagon import OddRCoord
from ....visual.asset_management.game_obj_to_sprite_registry import TILE_SPRITE_METADATA
from ....visual.asset_management.spritesheet_manager import SpritesheetManager
from ..spatial_component import SpatialComponent
from ..hitbox import HexHitbox
from ....visual.asset_management.visual_component import VisualComponent
from ....visual.asset_management.spritesheet_structure import SpritesheetComponent
from .....event_tokens.payloads import TilePayload
from ....visual.asset_management.sprite_key_registry import TYPICAL_TILE_SIZE

import pygame


class TileElement(ElementWrapper):
    def __init__(self, tile: Tile, camera: Camera):
        sprite_metadata = TILE_SPRITE_METADATA[0]
        spritesheet_name = SpritesheetManager.register_spritesheet(
            sprite_metadata
        ).get_key()

        super().__init__(
            registered_name=f"tile_{id(tile)}",
            grouping_name="TILE",
            camera=camera,
            spatial_component=SpatialComponent(
                TileElement._define_tile_rect(tile), space_mode="WORLD"
            ),
            interactable_component=HexHitbox(),
            visual_component=VisualComponent(
                SpritesheetComponent(spritesheet_reference=spritesheet_name),
                "NONE",
            ),
            payload=TilePayload(tile),
        )

    @classmethod
    def _define_tile_rect(cls, tile: Tile) -> pygame.Rect:
        """Given a Tile, return its bounding rectangle as (x, y, width, height)."""
        pixel_x, pixel_y = tile.coord.to_pixel(*TYPICAL_TILE_SIZE, is_bounding_box=True)
        width, height = TYPICAL_TILE_SIZE
        return pygame.Rect((pixel_x, pixel_y, width, height))

    def get_coord(self) -> OddRCoord:
        assert isinstance(self.payload, TilePayload)
        return self.payload.tile.coord
