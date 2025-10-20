from ..element import ElementWrapper
from ..spatial_component import Camera
from ratroyale.backend.tile import Tile
from ratroyale.backend.hexagon import OddRCoord
from ..spatial_component import SpatialComponent
from ..hitbox import HexHitbox
from ....visual.asset_management.visual_component import VisualComponent
from ....visual.asset_management.spritesheet_structure import SpritesheetComponent
from .....event_tokens.payloads import TilePayload
from ....visual.anim.presets.presets import (
    on_select_color_fade_in,
    on_select_color_fade_out,
)
from ....visual.asset_management.sprite_key_registry import TYPICAL_TILE_SIZE

import pygame


class TileMaskElement(ElementWrapper):
    def __init__(
        self,
        tile: Tile,
        camera: Camera,
        grouping_name: str,
        z_order: int,
        mask_color: pygame.Color,
    ):
        rect = TileMaskElement._define_tile_rect(tile)
        surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 1))
        self.mask_color = mask_color

        super().__init__(
            registered_name=f"{grouping_name}_{id(tile)}",
            grouping_name=grouping_name,
            camera=camera,
            spatial_component=SpatialComponent(
                rect,
                space_mode="WORLD",
                z_order=z_order,
            ),
            interactable_component=HexHitbox(),
            visual_component=VisualComponent(
                SpritesheetComponent(spritesheet_reference=surf),
                "NONE",
            ),
            payload=TilePayload(tile),
            is_blocking=False,
        )

    @classmethod
    def _define_tile_rect(cls, tile: Tile) -> pygame.Rect:
        """Given a Tile, return its bounding rectangle as (x, y, width, height)."""
        pixel_x, pixel_y = tile.coord.to_pixel(*TYPICAL_TILE_SIZE, is_bounding_box=True)
        width, height = TYPICAL_TILE_SIZE
        return pygame.Rect((pixel_x, pixel_y, width, height))

    def on_select(self) -> bool:
        vis = self.visual_component
        if vis and vis.spritesheet_component:
            vis.queue_override_animation(
                on_select_color_fade_in(
                    vis.spritesheet_component,
                    color=self.mask_color,
                )
            )

        return True

    def on_deselect(self) -> bool:
        vis = self.visual_component
        if vis and vis.spritesheet_component:
            vis.queue_override_animation(
                on_select_color_fade_out(
                    vis.spritesheet_component,
                    color=self.mask_color,
                )
            )

        return True

    def get_coord(self) -> OddRCoord:
        assert isinstance(self.payload, TilePayload)
        return self.payload.tile.coord
