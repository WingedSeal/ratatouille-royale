from ..element import ElementWrapper
from ..spatial_component import Camera
from ratroyale.backend.entity import Entity
from ....visual.asset_management.game_obj_to_sprite_registry import (
    SPRITE_METADATA_REGISTRY,
    TYPICAL_TILE_SIZE,
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
        """Given an Entity, return its bounding rectangle as (x, y, width, height).
        Assumes pos.to_pixel() returns the *center* of the hex tile.
        """
        pixel_x, pixel_y = EntityElement._define_position(entity.pos)
        width, height = cls._ENTITY_WIDTH_HEIGHT

        # Shift from center to top-left
        top_left_x = pixel_x - width / 2
        top_left_y = pixel_y - height / 2

        return pygame.Rect(top_left_x, top_left_y, width, height)

    @classmethod
    def _define_position(cls, pos: OddRCoord) -> tuple[float, float]:
        """Return the *center* pixel position of an entity on the hex grid.
        Adjusts based on tile and entity dimensions.
        """
        # Get hex center
        pixel_x, pixel_y = pos.to_pixel(*TYPICAL_TILE_SIZE, is_bounding_box=True)
        tile_w, tile_h = TYPICAL_TILE_SIZE
        ent_w, ent_h = cls._ENTITY_WIDTH_HEIGHT

        # Center the entity relative to the hex center
        # (so a smaller entity stays centered on its tile)
        pixel_x += (tile_w - ent_w) / 2 - tile_w / 2
        pixel_y += (tile_h - ent_h) / 2 - tile_h / 2

        return pixel_x + ent_w / 2, pixel_y + ent_h / 2

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
        visual_component = self.visual_component
        if visual_component and visual_component.spritesheet_component:

            for pos in pos_sequence:
                anim = move_entity(
                    target_pos=EntityElement._define_position(pos),
                    spatial=self.spatial_component,
                    camera=self.camera,
                )
                visual_component.queue_override_animation(anim)

        return True

    def on_hurt(self) -> bool:
        visual_component = self.visual_component
        if visual_component and visual_component.spritesheet_component:
            anim = entity_hurt(
                visual_component.spritesheet_component, pygame.Color(255, 0, 0)
            )
            visual_component.queue_override_animation(anim)

        self.update_health()

        return True

    def on_select(self) -> bool:
        visual_component = self.visual_component
        if visual_component and visual_component.spritesheet_component:
            visual_component.queue_override_animation(
                on_select_color_fade_in(
                    visual_component.spritesheet_component,
                    color=pygame.Color(200, 200, 0),
                )
            )

        return True

    def on_deselect(self) -> bool:
        visual_component = self.visual_component
        if visual_component and visual_component.spritesheet_component:
            visual_component.queue_override_animation(
                on_select_color_fade_out(
                    visual_component.spritesheet_component,
                    color=pygame.Color(200, 200, 0),
                )
            )

        return True

    def update_health(self) -> None:
        hp_text = italic_bold_arial.render(
            "HP: " + str(self.entity.health), False, pygame.Color(255, 255, 255)
        )
        hp_element = self.children[0]
        visual_component = hp_element.visual_component
        if visual_component and visual_component.spritesheet_component:
            visual_component.spritesheet_component.spritesheet_reference = hp_text
