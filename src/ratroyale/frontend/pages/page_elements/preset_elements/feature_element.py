from ..element import ElementWrapper
from ..spatial_component import Camera
from ratroyale.backend.feature import Feature
from ratroyale.backend.hexagon import OddRCoord
from ....visual.asset_management.game_obj_to_sprite_registry import (
    FEATURE_SPRITE_METADATA,
)
from ....visual.asset_management.spritesheet_manager import SpritesheetManager
from ..spatial_component import SpatialComponent
from ..hitbox import HexHitbox
from ....visual.asset_management.visual_component import VisualComponent
from ....visual.asset_management.spritesheet_structure import SpritesheetComponent
from .....event_tokens.payloads import TilePayload
from ....visual.asset_management.sprite_key_registry import TYPICAL_TILE_SIZE
import uuid

import pygame


class FeatureElement(ElementWrapper):
    def __init__(self, feature: Feature, coord: OddRCoord, camera: Camera):
        print(feature.FEATURE_ID())
        sprite_metadata = FEATURE_SPRITE_METADATA[feature.FEATURE_ID()]
        spritesheet_name = SpritesheetManager.register_spritesheet(
            sprite_metadata
        ).get_key()

        super().__init__(
            registered_name=f"feature_{id(feature)}_portion_{uuid.uuid4()}",
            grouping_name="FEATURE",
            camera=camera,
            spatial_component=SpatialComponent(
                FeatureElement._define_tile_rect(coord), space_mode="WORLD", z_order=5
            ),
            interactable_component=HexHitbox(),
            visual_component=VisualComponent(
                SpritesheetComponent(spritesheet_reference=spritesheet_name),
                "NONE",
            ),
        )

    @classmethod
    def _define_tile_rect(cls, coord: OddRCoord) -> pygame.Rect:
        """Given a Tile, return its bounding rectangle as (x, y, width, height)."""
        pixel_x, pixel_y = coord.to_pixel(*TYPICAL_TILE_SIZE, is_bounding_box=True)
        width, height = TYPICAL_TILE_SIZE
        return pygame.Rect((pixel_x, pixel_y, width, height))

    def get_coord(self) -> OddRCoord:
        assert isinstance(self.payload, TilePayload)
        return self.payload.tile.coord
