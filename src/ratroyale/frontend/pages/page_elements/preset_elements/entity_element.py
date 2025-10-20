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
    move_entity,
    entity_hurt,
)
from ....visual.asset_management.sprite_key_registry import TYPICAL_TILE_SIZE
from .....backend.hexagon import OddRCoord

import pygame
import uuid


# Load a font, size 48, italic
italic_bold_arial = pygame.font.SysFont("Arial", 48, bold=True, italic=True)


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
                z_order=10,
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
        pixel_x, pixel_y = EntityElement._define_position(entity.pos)
        return pygame.Rect((pixel_x, pixel_y, *cls._ENTITY_WIDTH_HEIGHT))

    @classmethod
    def _define_position(cls, pos: OddRCoord) -> tuple[float, float]:
        pixel_x, pixel_y = pos.to_pixel(*TYPICAL_TILE_SIZE, is_bounding_box=True)
        width, height = cls._ENTITY_WIDTH_HEIGHT
        pixel_x += (TYPICAL_TILE_SIZE[0] - width) / 2
        pixel_y += (TYPICAL_TILE_SIZE[1] - height) / 2
        return pixel_x, pixel_y

    def _temp_stat_generators(self) -> list[ElementWrapper]:
        elements = []

        hp_text = italic_bold_arial.render(
            "HP: " + str(self.entity.health), False, pygame.Color(255, 255, 255)
        )
        hp_element = ElementWrapper(
            registered_name="hpElement_" + str(uuid.uuid4()),
            grouping_name="HPELEMENT",
            camera=self.camera,
            spatial_component=SpatialComponent(
                pygame.Rect(0, 40, 50, 20),
                space_mode="WORLD",
                z_order=11,
            ),
            visual_component=VisualComponent(
                SpritesheetComponent(spritesheet_reference=hp_text)
            ),
            parent_element=self.registered_name,
        )
        elements.append(hp_element)

        side_text = italic_bold_arial.render(
            str(self.entity.side), False, pygame.Color(255, 255, 255)
        )
        side_element = ElementWrapper(
            registered_name="side_" + str(uuid.uuid4()),
            grouping_name="SIDE",
            camera=self.camera,
            spatial_component=SpatialComponent(
                pygame.Rect(0, 60, 70, 20),
                space_mode="WORLD",
                z_order=11,
            ),
            visual_component=VisualComponent(
                SpritesheetComponent(spritesheet_reference=side_text)
            ),
            parent_element=self.registered_name,
        )
        elements.append(side_element)

        name_text = italic_bold_arial.render(
            str(self.entity.name), False, pygame.Color(255, 255, 255)
        )
        side_element = ElementWrapper(
            registered_name="side_" + str(uuid.uuid4()),
            grouping_name="SIDE",
            camera=self.camera,
            spatial_component=SpatialComponent(
                pygame.Rect(0, 80, 70, 20),
                space_mode="WORLD",
                z_order=11,
            ),
            visual_component=VisualComponent(
                SpritesheetComponent(spritesheet_reference=name_text)
            ),
            parent_element=self.registered_name,
        )
        elements.append(side_element)

        return elements

    def move_entity(self, pos_sequence: list[OddRCoord]) -> bool:
        """
        Queue movement animations for an entity along a sequence of positions,
        moving from each position to the next.
        """
        vis = self.visual_component
        if vis and vis.spritesheet_component:

            for pos in pos_sequence:
                anim = move_entity(
                    target_pos=EntityElement._define_position(pos),
                    spatial=self.spatial_component,
                    camera=self.camera,
                )
                vis.queue_override_animation(anim)

        return True

    def on_hurt(self) -> bool:
        vis = self.visual_component
        if vis and vis.spritesheet_component:
            anim = entity_hurt(vis.spritesheet_component, pygame.Color(255, 0, 0))
            vis.queue_override_animation(anim)

        self.update_health()

        return True

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

    def update_health(self) -> None:
        hp_text = italic_bold_arial.render(
            "HP: " + str(self.entity.health), False, pygame.Color(255, 255, 255)
        )
        hp_element = self.children[0]
        vis = hp_element.visual_component
        if vis and vis.spritesheet_component:
            vis.spritesheet_component.spritesheet_reference = hp_text
