from ..element import ElementWrapper
from ..spatial_component import Camera
from ratroyale.backend.feature import Feature
from ratroyale.backend.hexagon import OddRCoord
from ....visual.asset_management.game_obj_to_sprite_registry import (
    DUMMY_TEXTURE_METADATA,
    FEATURE_SPRITE_METADATA,
    TYPICAL_TILE_SIZE,
)
from ....visual.asset_management.spritesheet_manager import SpritesheetManager
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

import pygame

# Load a font, size 48, italic
italic_bold_arial = pygame.font.SysFont("Arial", 30, bold=True, italic=True)


class FeatureElement(ElementWrapper):
    def __init__(self, feature: Feature, coord: OddRCoord, camera: Camera):
        sprite_metadata = FEATURE_SPRITE_METADATA.get(
            feature.FEATURE_ID(), DUMMY_TEXTURE_METADATA
        )
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
