from ..element import ElementWrapper
from ..spatial_component import Camera
from ratroyale.backend.tile import Tile
from ....visual.asset_management.game_obj_to_sprite_registry import (
    TILE_SPRITE_METADATA,
    TYPICAL_TILE_SIZE,
)
from ....visual.asset_management.spritesheet_manager import SpritesheetManager
from ..spatial_component import SpatialComponent
from ....visual.asset_management.visual_component import VisualComponent
from ....visual.asset_management.spritesheet_structure import SpritesheetComponent
import uuid
from ...page_elements.hitbox import RectangleHitbox

import pygame


class ChunkedTileMapElement(ElementWrapper):
    def __init__(self, tile_grid: list[list[Tile | None]], camera: Camera):
        self._camera = camera
        self._tile_grid = tile_grid

        # Flatten non-None tiles to compute bounds
        tiles_flat = [tile for row in tile_grid for tile in row if tile is not None]
        self._map_rect = self._compute_map_rect(tiles_flat)

        # Pre-render surface for this chunk
        self._chunk_surface = pygame.Surface(self._map_rect.size, pygame.SRCALPHA)

        for tile in tiles_flat:
            tile_rect = self._define_tile_rect(tile)

            # Offset relative to chunk surface
            local_tile_rect = tile_rect.copy()
            local_tile_rect.topleft = (
                tile_rect.x - self._map_rect.x,
                tile_rect.y - self._map_rect.y,
            )

            # Get spritesheet/frame
            sprite_metadata = TILE_SPRITE_METADATA[tile.tile_id]
            spritesheet_name = SpritesheetManager.register_spritesheet(
                sprite_metadata
            ).get_key()
            visual = VisualComponent(
                SpritesheetComponent(spritesheet_reference=spritesheet_name), "NONE"
            )
            assert visual.spritesheet_component
            frame = visual.spritesheet_component.output_frame(
                tile_rect, camera=self._camera
            )
            if frame:
                self._chunk_surface.blit(frame, local_tile_rect.topleft)

        # Use a simple visual component that just blits the pre-rendered surface
        visual_component = VisualComponent(
            SpritesheetComponent(self._chunk_surface), "NONE"
        )

        # Initialize the ElementWrapper
        super().__init__(
            registered_name=f"tile_chunk_{uuid.uuid4()}",
            grouping_name="TILEMAP",
            camera=camera,
            spatial_component=SpatialComponent(
                self._map_rect, space_mode="WORLD", z_order=1
            ),
            interactable_component=RectangleHitbox(),
            visual_component=visual_component,
            payload=None,
            is_blocking=True,
        )

    @staticmethod
    def _define_tile_rect(tile: Tile) -> pygame.Rect:
        width, height = TYPICAL_TILE_SIZE
        pixel_x, pixel_y = tile.coord.to_pixel(width, height, is_bounding_box=True)
        top_left_x = pixel_x - width / 2
        top_left_y = pixel_y - height / 2
        return pygame.Rect(top_left_x, top_left_y, width, height)

    @staticmethod
    def _compute_map_rect(tiles: list[Tile]) -> pygame.Rect:
        rects = [ChunkedTileMapElement._define_tile_rect(tile) for tile in tiles]
        if not rects:
            return pygame.Rect(0, 0, 0, 0)
        min_x = min(r.left for r in rects)
        min_y = min(r.top for r in rects)
        max_x = max(r.right for r in rects)
        max_y = max(r.bottom for r in rects)
        return pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
