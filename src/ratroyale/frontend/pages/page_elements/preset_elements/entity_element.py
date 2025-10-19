from ..element import ElementWrapper
from ..spatial_component import Camera
from ratroyale.backend.entity import Entity
from ....visual.asset_management.game_obj_to_sprite_registry import (
    SPRITE_METADATA_REGISTRY,
)
from ....visual.asset_management.spritesheet_manager import SpritesheetManager
from ..spatial_component import SpatialComponent
from ..hitbox import RectangleHitbox
from ....visual.asset_management.visual_component import VisualComponent
from ....visual.asset_management.spritesheet_structure import SpritesheetComponent
from .....event_tokens.payloads import EntityPayload
from ....visual.anim.presets.presets import (
    default_idle_for_entity,
    on_select_color_fade_in,
    on_select_color_fade_out,
)
from ....visual.asset_management.sprite_key_registry import TYPICAL_TILE_SIZE

import pygame


class EntityElement(ElementWrapper):
    _ENTITY_WIDTH_HEIGHT = (50, 50)

    def __init__(self, entity: Entity, camera: Camera):
        # Register spritesheet
        sprite_metadata = SPRITE_METADATA_REGISTRY[type(entity)]
        spritesheet_name = SpritesheetManager.register_spritesheet(
            sprite_metadata
        ).get_key()
        spritesheet_component = SpritesheetComponent(spritesheet_name)

        # Build visual component
        visual_component = VisualComponent(spritesheet_component, "IDLE")
        visual_component.set_default_animation(
            default_idle_for_entity(spritesheet_component)
        )

        # Initialize base element
        super().__init__(
            registered_name=f"entity_{id(entity)}",
            grouping_name="ENTITY",
            camera=camera,
            spatial_component=SpatialComponent(
                self._define_entity_rect(entity),
                space_mode="WORLD",
                z_order=1,
            ),
            interactable_component=RectangleHitbox(),
            visual_component=visual_component,
            payload=EntityPayload(entity),
        )

        # --- EntityElement specific state ---
        self.entity = entity
        self._selected = False
        self._hovered = False

    @classmethod
    def entity_width_height(cls) -> tuple[float, float]:
        return cls._ENTITY_WIDTH_HEIGHT

    @classmethod
    def _define_entity_rect(cls, entity: Entity) -> pygame.Rect:
        """Given an Entity, return its bounding rectangle as (x, y, width, height)."""
        pixel_x, pixel_y = entity.pos.to_pixel(*TYPICAL_TILE_SIZE, is_bounding_box=True)
        width, height = cls._ENTITY_WIDTH_HEIGHT
        pixel_x += (TYPICAL_TILE_SIZE[0] - width) / 2
        pixel_y += (TYPICAL_TILE_SIZE[1] - height) / 2
        return pygame.Rect((pixel_x, pixel_y, width, height))

    def on_select(self) -> bool:
        vis = self.visual_component
        if vis and vis.spritesheet_component:
            vis.queue_override_animation(
                on_select_color_fade_in(
                    vis.spritesheet_component,
                    color=pygame.Color(200, 200, 0),
                )
            )

        return True

    def on_deselect(self) -> bool:
        vis = self.visual_component
        if vis and vis.spritesheet_component:
            vis.queue_override_animation(
                on_select_color_fade_out(
                    vis.spritesheet_component,
                    color=pygame.Color(200, 200, 0),
                )
            )

        return True
