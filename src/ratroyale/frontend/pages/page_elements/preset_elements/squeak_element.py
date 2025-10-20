from ..element import ElementWrapper
from ratroyale.backend.player_info.squeak import Squeak
from ....visual.asset_management.game_obj_to_sprite_registry import (
    SQUEAK_IMAGE_METADATA_REGISTRY,
)
from ....visual.asset_management.spritesheet_manager import SpritesheetManager
from ..spatial_component import SpatialComponent
from ..hitbox import RectangleHitbox
from ....visual.asset_management.visual_component import VisualComponent
from ....visual.asset_management.spritesheet_structure import SpritesheetComponent
from .....event_tokens.payloads import SqueakPayload
from ....visual.anim.presets.presets import return_squeak_to_normal, shrink_squeak
from ....pages.page_elements.spatial_component import Camera

import uuid

import pygame

PADDING = 5  # padding for cost text

SQUEAK_WIDTH, SQUEAK_HEIGHT = 112, 70
SQUEAK_SPACING = 5
LEFT_MARGIN = 0
TOP_MARGIN = 80

CARD_RECT = pygame.Rect(LEFT_MARGIN, TOP_MARGIN, SQUEAK_WIDTH, SQUEAK_HEIGHT)


class SqueakElement(ElementWrapper):
    """Encapsulates a squeak card + cost element."""

    def __init__(
        self, squeak: Squeak, index: int, camera: Camera, font: pygame.Font
    ) -> None:
        self.camera = camera
        self.font = font

        # --- Create main squeak element ---
        assert squeak.rodent
        # TODO: replace random with smth better
        self.squeak_element_id = f"squeak_{uuid.uuid4()}"
        sprite_metadata = SQUEAK_IMAGE_METADATA_REGISTRY[squeak.rodent]
        cached_spritesheet_name = SpritesheetManager.register_spritesheet(
            sprite_metadata
        ).get_key()

        card_rect = CARD_RECT.copy()
        card_rect.y += index * (SQUEAK_HEIGHT + SQUEAK_SPACING)

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
            SQUEAK_WIDTH - cost_width - PADDING,
            SQUEAK_HEIGHT - cost_height - PADDING,
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

    def decide_interactivity(self, current_crumb: int) -> None:
        squeak = self.payload
        assert isinstance(squeak, SqueakPayload)
        higher_cost_than_current_crumb = squeak.squeak.crumb_cost > current_crumb
        # is_previously_interactable = self.is_interactable
        self.is_interactable = not higher_cost_than_current_crumb
        # is_now_interactable = self.is_interactable

        # TODO: add darkening/undarkening anim

    def return_to_position(self, target_rect: pygame.Rect | pygame.FRect) -> None:
        spatial = self.spatial_component
        vis = self.visual_component
        if vis:
            vis.queue_override_animation(
                return_squeak_to_normal(
                    spatial, self.camera, target_rect.topleft, CARD_RECT.size
                )
            )

    def on_select(self) -> bool:
        vis = self.visual_component
        spatial = self.spatial_component
        if vis and vis.spritesheet_component:
            vis.queue_override_animation(shrink_squeak(spatial, self.camera))
        return True

    def on_deselect(self) -> bool:
        return True
