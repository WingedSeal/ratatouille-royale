from ..element import ElementWrapper
from ..spatial_component import Camera
from ratroyale.backend.entity import Entity
from ratroyale.backend.entities.rodent import Rodent
from ....visual.asset_management.game_obj_to_sprite_registry import (
    SPRITE_METADATA_REGISTRY,
    TYPICAL_TILE_SIZE,
    MISC_SPRITE_METADATA,
)

from ....visual.anim.core.anim_structure import SequentialAnim
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
    entity_spawn,
    entity_die,
    hurt_particle_motion,
)
from .....backend.hexagon import OddRCoord

import pygame
import uuid


# Load a font, size 48, italic
italic_bold_arial = pygame.font.SysFont("Arial", 30, bold=True, italic=True)


class EntityElement(ElementWrapper):
    _ENTITY_NORMAL_WIDTH_HEIGHT = (50, 50)
    _ENTITY_STARTING_WIDTH_HEIGHT = (1, 1)

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

        # --- Reference to updatable child elemenets (hp number & move stamina number)
        self.hp_number_text_ref = "hpText_" + str(uuid.uuid4())
        self.stamina_number_text_ref = "staminaText_" + str(uuid.uuid4())

        # --- EntityElement specific state ---
        self.entity = entity
        self._selected = False
        self._hovered = False

    @classmethod
    def entity_width_height(cls) -> tuple[float, float]:
        return cls._ENTITY_NORMAL_WIDTH_HEIGHT

    @classmethod
    def _define_entity_rect(cls, entity: Entity) -> pygame.Rect:
        """Given an Entity, return its bounding rectangle as (x, y, width, height).
        Assumes pos.to_pixel() returns the *center* of the hex tile.
        """
        pixel_x, pixel_y = EntityElement._define_position(entity.pos, True)
        width, height = cls._ENTITY_STARTING_WIDTH_HEIGHT

        return pygame.Rect(pixel_x, pixel_y, width, height)

    @classmethod
    def _define_position(
        cls, pos: OddRCoord, on_spawn: bool = False
    ) -> tuple[float, float]:
        """Return the *center* pixel position of an entity on the hex grid.
        Adjusts based on tile and entity dimensions.
        """
        # Get hex center
        pixel_x, pixel_y = pos.to_pixel(*TYPICAL_TILE_SIZE, is_bounding_box=True)
        tile_w, tile_h = TYPICAL_TILE_SIZE
        if on_spawn:
            ent_w, ent_h = cls._ENTITY_STARTING_WIDTH_HEIGHT
        else:
            ent_w, ent_h = cls._ENTITY_NORMAL_WIDTH_HEIGHT

        # Center the entity relative to the hex center
        # (so a smaller entity stays centered on its tile)
        pixel_x += (tile_w - ent_w) / 2 - tile_w / 2
        pixel_y += (tile_h - ent_h) / 2 - tile_h / 2

        return pixel_x, pixel_y

    def stat_elements(self) -> list[ElementWrapper]:
        elements: list[ElementWrapper] = []

        hp_element = self.health_element()
        elements += hp_element

        if isinstance(self.entity, Rodent):
            move_stamina_element = self.move_stamina_element()
            elements += move_stamina_element

        side_text = italic_bold_arial.render(
            str(self.entity.side)[5:], False, pygame.Color("white")
        )
        side_element = ElementWrapper(
            registered_name="side_" + str(uuid.uuid4()),
            grouping_name="SIDE",
            camera=self.camera,
            spatial_component=SpatialComponent(
                pygame.Rect(0, -30, side_text.width, side_text.height),
                space_mode="WORLD",
                z_order=11,
            ),
            visual_component=VisualComponent(
                SpritesheetComponent(spritesheet_reference=side_text)
            ),
            parent_element=self.registered_name,
        )
        elements.append(side_element)

        return elements

    def health_element(self) -> list[ElementWrapper]:
        sprite_metadata = MISC_SPRITE_METADATA["HealthIcon"]
        spritesheet_name = SpritesheetManager.register_spritesheet(
            sprite_metadata
        ).get_key()
        spritesheet_component = SpritesheetComponent(spritesheet_name)

        # Base icon visual
        hp_icon_rect = pygame.Rect(0, 40, 30, 27)
        hp_icon_element = ElementWrapper(
            registered_name="hpIcon_" + str(uuid.uuid4()),
            grouping_name="HPELEMENT",
            camera=self.camera,
            spatial_component=SpatialComponent(
                hp_icon_rect,
                space_mode="WORLD",
                z_order=11,
            ),
            visual_component=VisualComponent(spritesheet_component, "NONE"),
            parent_element=self.registered_name,
        )

        # Render health text
        hp_text_surface = italic_bold_arial.render(
            str(self.entity.health), False, pygame.Color("white")
        )

        # Compute centered position within icon rect
        text_width = hp_icon_rect.width * 0.5
        text_height = hp_icon_rect.height * 0.8
        text_x = hp_icon_rect.x + (hp_icon_rect.width - text_width) // 2
        text_y = hp_icon_rect.y - (hp_icon_rect.height - text_height) // 2
        hp_text_rect = pygame.Rect(text_x, text_y, text_width, text_height)

        hp_text_element = ElementWrapper(
            registered_name=self.hp_number_text_ref,
            grouping_name="HPELEMENT",
            camera=self.camera,
            spatial_component=SpatialComponent(
                hp_text_rect,
                space_mode="WORLD",
                z_order=12,  # one layer above icon
            ),
            visual_component=VisualComponent(SpritesheetComponent(hp_text_surface)),
            parent_element=self.registered_name,
        )

        return [hp_icon_element, hp_text_element]

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

    def move_stamina_element(self) -> list[ElementWrapper]:
        sprite_metadata = MISC_SPRITE_METADATA["MoveStaminaIcon"]
        spritesheet_name = SpritesheetManager.register_spritesheet(
            sprite_metadata
        ).get_key()
        spritesheet_component = SpritesheetComponent(spritesheet_name)

        # Base icon visual
        stamina_icon_rect = pygame.Rect(27, 40, 30, 27)
        stamina_icon_element = ElementWrapper(
            registered_name="staminaIcon_" + str(uuid.uuid4()),
            grouping_name="STAMINAELEMENT",
            camera=self.camera,
            spatial_component=SpatialComponent(
                stamina_icon_rect,
                space_mode="WORLD",
                z_order=11,
            ),
            visual_component=VisualComponent(spritesheet_component, "NONE"),
            parent_element=self.registered_name,
        )

        # Render stamina text
        assert isinstance(self.entity, Rodent)
        stamina_text_surface = italic_bold_arial.render(
            str(self.entity.move_stamina), False, pygame.Color("white")
        )

        # Compute centered position within icon rect
        text_width = stamina_icon_rect.width * 0.5
        text_height = stamina_icon_rect.height * 0.8
        text_x = stamina_icon_rect.x + (stamina_icon_rect.width - text_width) // 2
        text_y = stamina_icon_rect.y - (stamina_icon_rect.height - text_height) // 2
        stamina_text_rect = pygame.Rect(text_x, text_y, text_width, text_height)

        stamina_text_element = ElementWrapper(
            registered_name=self.stamina_number_text_ref,
            grouping_name="STAMINAELEMENT",
            camera=self.camera,
            spatial_component=SpatialComponent(
                stamina_text_rect,
                space_mode="WORLD",
                z_order=12,  # one layer above icon
            ),
            visual_component=VisualComponent(
                SpritesheetComponent(stamina_text_surface)
            ),
            parent_element=self.registered_name,
        )

        return [stamina_icon_element, stamina_text_element]

    def move_entity(
        self, pos_sequence: list[OddRCoord]
    ) -> list[tuple[ElementWrapper, SequentialAnim]]:
        """
        Queue movement animations for an entity along a sequence of positions,
        moving from each position to the next.
        """
        visual_component = self.visual_component
        anim_list: list[tuple[ElementWrapper, SequentialAnim]] = []
        if visual_component and visual_component.spritesheet_component:

            for pos in pos_sequence:
                anim = move_entity(
                    target_pos=EntityElement._define_position(pos),
                    spatial=self.spatial_component,
                    camera=self.camera,
                )
                anim_list.append((self, anim))

        return anim_list

    def on_spawn(self) -> tuple[ElementWrapper, SequentialAnim]:
        visual_component = self.visual_component
        if visual_component and visual_component.spritesheet_component:
            anim = entity_spawn(self.spatial_component, self.camera)

        return (self, anim)

    def on_hurt(self) -> tuple[ElementWrapper, SequentialAnim]:
        visual_component = self.visual_component
        if visual_component and visual_component.spritesheet_component:
            anim = entity_hurt(
                visual_component.spritesheet_component, pygame.Color(255, 0, 0)
            )

        self.update_health()

        return (self, anim)

    def on_die(self) -> tuple[ElementWrapper, SequentialAnim]:
        visual_component = self.visual_component
        if visual_component and visual_component.spritesheet_component:
            anim = entity_die(self, self.spatial_component, self.camera)

        return (self, anim)

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
            str(self.entity.health), False, pygame.Color("white")
        )
        hp_element = self.children[self.hp_number_text_ref]
        visual_component = hp_element.visual_component
        if visual_component and visual_component.spritesheet_component:
            visual_component.spritesheet_component.spritesheet_reference = hp_text

    def update_move_stamina(self) -> None:
        assert isinstance(self.entity, Rodent)
        stamina_text = italic_bold_arial.render(
            str(self.entity.move_stamina), False, pygame.Color("white")
        )
        stamina_text_element = self.children[self.stamina_number_text_ref]
        visual_component = stamina_text_element.visual_component
        if visual_component and visual_component.spritesheet_component:
            visual_component.spritesheet_component.spritesheet_reference = stamina_text
