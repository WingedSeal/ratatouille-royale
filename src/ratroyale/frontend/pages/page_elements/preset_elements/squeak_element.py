from ..element import ElementWrapper
from ratroyale.backend.player_info.squeak import Squeak
from ....visual.asset_management.game_obj_to_sprite_registry import (
    SQUEAK_IMAGE_METADATA_REGISTRY,
    DUMMY_TEXTURE_METADATA,
)
from ....visual.asset_management.spritesheet_manager import SpritesheetManager
from ..spatial_component import SpatialComponent
from ..hitbox import RectangleHitbox
from ....visual.asset_management.visual_component import VisualComponent
from ....visual.asset_management.spritesheet_structure import SpritesheetComponent
from .....event_tokens.payloads import SqueakPayload
from ....visual.anim.presets.presets import (
    return_squeak_to_normal,
    shrink_squeak,
    on_select_color_fade_in,
    on_select_color_fade_out,
)
from ....pages.page_elements.spatial_component import Camera
from ....visual.screen_constants import (
    SQUEAK_COST_PADDING,
    SQUEAK_SPACING,
    SQUEAK_SIZE,
    SQUEAK_RECT,
)

import uuid

import pygame


# Load a font, size 48, italic
italic_bold_arial = pygame.font.SysFont("Arial", 48, bold=True, italic=True)


class SqueakElement(ElementWrapper):
    """Encapsulates a squeak card + cost element."""

    def __init__(
        self, squeak: Squeak, index: int, camera: Camera, font: pygame.Font
    ) -> None:
        self.camera = camera
        self.font = font
        self.squeak = squeak
        self.can_be_played = True

        # --- Create main squeak element ---
        # TODO: replace random with smth better
        self.squeak_element_id = f"squeak_{uuid.uuid4()}"
        sprite_metadata = SQUEAK_IMAGE_METADATA_REGISTRY.get(
            squeak, DUMMY_TEXTURE_METADATA
        )

        cached_spritesheet_name = SpritesheetManager.register_spritesheet(
            sprite_metadata
        ).get_key()

        card_rect = SQUEAK_RECT.copy()
        card_rect.y += index * (SQUEAK_SIZE[1] + SQUEAK_SPACING)

        super().__init__(
            registered_name=self.squeak_element_id,
            grouping_name="SQUEAK",
            camera=camera,
            spatial_component=SpatialComponent(
                card_rect, space_mode="SCREEN", z_order=100
            ),
            interactable_component=RectangleHitbox(),
            is_blocking=False,
            visual_component=VisualComponent(
                SpritesheetComponent(spritesheet_reference=cached_spritesheet_name),
                "NONE",
            ),
            payload=SqueakPayload(index, squeak),
        )

    @property
    def ids(self) -> tuple[str, str]:
        """Return the main element id and cost element id."""
        assert isinstance(self.payload, SqueakPayload)
        return self.squeak_element_id, f"squeakCost_{id(self.payload.squeak)}"

    def create_cost_element(self) -> ElementWrapper:
        assert isinstance(self.payload, SqueakPayload)
        squeak = self.payload.squeak

        # Render cost text
        squeak_cost = squeak.crumb_cost
        squeak_cost_text = self.font.render(
            str(squeak_cost), False, pygame.Color(255, 255, 255)
        )
        # Compute cost rect anchored to bottom-right of card
        cost_width, cost_height = squeak_cost_text.get_size()

        # --- Local position relative to the card (bottom-right corner) ---
        cost_rect = pygame.Rect(
            SQUEAK_SIZE[0] - cost_width - SQUEAK_COST_PADDING,
            SQUEAK_SIZE[1] - cost_height - SQUEAK_COST_PADDING,
            cost_width,
            cost_height,
        )

        return ElementWrapper(
            registered_name=f"squeakCost_{uuid.uuid4()}",
            grouping_name="SQUEAKCOST",
            camera=self.camera,
            spatial_component=SpatialComponent(
                cost_rect, space_mode="SCREEN", z_order=101
            ),
            interactable_component=None,
            is_blocking=False,
            visual_component=VisualComponent(
                SpritesheetComponent(spritesheet_reference=squeak_cost_text), "NONE"
            ),
            parent_element=self.squeak_element_id,
        )

    def _temp_name_generator(self) -> ElementWrapper:
        name_text = italic_bold_arial.render(
            str(self.squeak.name), False, pygame.Color(255, 255, 255)
        )
        name_element = ElementWrapper(
            registered_name="squeakname_" + str(uuid.uuid4()),
            grouping_name="SQUEAKNAME",
            camera=self.camera,
            spatial_component=SpatialComponent(
                pygame.Rect(0, 20, 70, 20),
                space_mode="SCREEN",
                z_order=101,
            ),
            visual_component=VisualComponent(
                SpritesheetComponent(spritesheet_reference=name_text), "NONE"
            ),
            parent_element=self.squeak_element_id,
        )
        return name_element

    def decide_interactivity(self, current_crumb: int) -> None:
        squeak = self.payload
        assert isinstance(squeak, SqueakPayload)

        higher_cost_than_current_crumb = squeak.squeak.crumb_cost > current_crumb
        is_previously_playable = self.can_be_played

        # Update interactivity state
        self.can_be_played = not higher_cost_than_current_crumb
        is_now_interactable = self.can_be_played

        # If state changed, trigger appropriate animation
        if is_now_interactable != is_previously_playable:
            if is_now_interactable:
                self.enable_anim()
            else:
                self.disable_anim()

    def enable_anim(self) -> None:
        visual_component = self.visual_component
        if visual_component and visual_component.spritesheet_component:
            visual_component.queue_override_animation(
                on_select_color_fade_out(
                    visual_component.spritesheet_component,
                    pygame.Color(200, 200, 200),
                    pygame.BLEND_RGB_SUB,
                )
            )

    def disable_anim(self) -> None:
        visual_component = self.visual_component
        if visual_component and visual_component.spritesheet_component:
            visual_component.queue_override_animation(
                on_select_color_fade_in(
                    visual_component.spritesheet_component,
                    pygame.Color(200, 200, 200),
                    pygame.BLEND_RGB_SUB,
                )
            )

    def move_to_position(self, target_rect: pygame.Rect | pygame.FRect) -> None:
        spatial = self.spatial_component
        visual_component = self.visual_component
        if visual_component:
            visual_component.queue_override_animation(
                return_squeak_to_normal(
                    spatial, self.camera, target_rect.topleft, SQUEAK_RECT.size
                )
            )

    def on_select(self) -> bool:
        visual_component = self.visual_component
        spatial = self.spatial_component
        if visual_component and visual_component.spritesheet_component:
            visual_component.queue_override_animation(
                shrink_squeak(spatial, self.camera)
            )
        return True

    def on_deselect(self) -> bool:
        return True
