from ..element import ElementWrapper
from ..spatial_component import Camera
from ratroyale.backend.feature import Feature
from ratroyale.backend.hexagon import OddRCoord
from ....visual.asset_management.game_obj_to_sprite_registry import (
    TYPICAL_TILE_SIZE,
    FEATURE_SPRITE_PATH,
    RED_LAIR_PATH,
    BLUE_LAIR_PATH,
)
from ....visual.anim.core.anim_structure import SequentialAnim
from ..spatial_component import SpatialComponent
from ..hitbox import HexHitbox
from ....visual.asset_management.visual_component import VisualComponent
from ....visual.asset_management.spritesheet_structure import SpritesheetComponent
from .....event_tokens.payloads import TilePayload
import uuid
from ....visual.anim.presets.presets import (
    feature_damaged,
    entity_die,
    hurt_particle_motion,
)
from ....feature_texture import generate_feature_surface, load_three_tiles
from ratroyale.backend.side import Side

import pygame

# Load a font, size 48, italic
italic_bold_arial = pygame.font.SysFont("Arial", 30, bold=True, italic=True)


class FeatureElement(ElementWrapper):
    def __init__(self, feature: Feature, coord: OddRCoord, camera: Camera):
        relative_shape, origin = feature.get_relative_shape_and_origin()
        feature_id = feature.FEATURE_ID()

        if feature_id == 1:
            if feature.side == Side.RAT:
                feature_surface = generate_feature_surface(
                    origin,
                    relative_shape,
                    load_three_tiles(RED_LAIR_PATH),
                    TYPICAL_TILE_SIZE[0],
                    is_bounding_box=True,
                )
            else:
                feature_surface = generate_feature_surface(
                    origin,
                    relative_shape,
                    load_three_tiles(BLUE_LAIR_PATH),
                    TYPICAL_TILE_SIZE[0],
                    is_bounding_box=True,
                )
        else:
            feature_surface = generate_feature_surface(
                origin,
                relative_shape,
                load_three_tiles(FEATURE_SPRITE_PATH[feature_id]),
                TYPICAL_TILE_SIZE[0],
                is_bounding_box=True,
            )
        # print(
        #     feature.get_name_and_description()[0],
        #     relative_shape,
        #     origin,
        #     feature.shape[0],
        # )
        super().__init__(
            registered_name=f"feature_{id(feature)}_portion_{uuid.uuid4()}",
            grouping_name="FEATURE",
            camera=camera,
            spatial_component=SpatialComponent(
                FeatureElement._compute_map_rect(feature), space_mode="WORLD", z_order=5
            ),
            interactable_component=HexHitbox(),
            visual_component=VisualComponent(
                SpritesheetComponent(spritesheet_reference=feature_surface),
                "NONE",
            ),
        )

    @classmethod
    def _define_tile_rect(cls, coord: OddRCoord) -> pygame.Rect:
        """Given a Tile, return its bounding rectangle as (x, y, width, height).
        Assumes tile.coord.to_pixel() returns the *center* of the hex tile.
        """
        width, height = TYPICAL_TILE_SIZE
        pixel_x, pixel_y = coord.to_pixel(width, height, is_bounding_box=True)

        # Shift from center → top-left of bounding box
        top_left_x = pixel_x - width / 2
        top_left_y = pixel_y - height / 2

        return pygame.Rect(top_left_x, top_left_y, width, height)

    def get_coord(self) -> OddRCoord:
        assert isinstance(self.payload, TilePayload)
        return self.payload.tile.coord

    def on_damaged(self) -> tuple[ElementWrapper, SequentialAnim]:
        visual_component = self.visual_component
        assert visual_component and visual_component.spritesheet_component
        anim = feature_damaged(
            visual_component.spritesheet_component, pygame.Color(255, 0, 0)
        )
        return (self, anim)

    def hurt_particle(self, hp_loss: int) -> ElementWrapper:
        # Render health text
        hurt_particle_surface = italic_bold_arial.render(
            "-" + str(hp_loss), False, pygame.Color("red")
        )
        hurt_particle_rect = hurt_particle_surface.get_rect()

        hurt_particle_element = ElementWrapper(
            registered_name="hpLossParticle_" + str(uuid.uuid4()),
            grouping_name="PARTICLE",
            camera=self.camera,
            spatial_component=SpatialComponent(
                hurt_particle_rect,
                space_mode="WORLD",
                z_order=100,  # one layer above icon
            ),
            visual_component=VisualComponent(
                SpritesheetComponent(hurt_particle_surface)
            ),
            parent_element=self.registered_name,
        )

        anim = hurt_particle_motion(hurt_particle_element)
        hurt_particle_element.queue_override_animation(anim)

        return hurt_particle_element

    def on_die(self) -> tuple[ElementWrapper, SequentialAnim]:
        visual_component = self.visual_component
        assert visual_component and visual_component.spritesheet_component
        anim = entity_die(self, self.spatial_component, self.camera)

        return (self, anim)

    @staticmethod
    def _compute_map_rect(feature: Feature) -> pygame.Rect:
        rects = [FeatureElement._define_tile_rect(tile) for tile in feature.shape]
        if not rects:
            return pygame.Rect(0, 0, 0, 0)
        min_x = min(r.left for r in rects)
        min_y = min(r.top for r in rects)
        max_x = max(r.right for r in rects)
        max_y = max(r.bottom for r in rects)
        return pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
