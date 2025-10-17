import pygame

from ratroyale.backend.board import Board
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.visual_token import *
from ratroyale.frontend.gesture.gesture_data import GestureType
from ratroyale.event_tokens.input_token import get_id, get_gesture_data

from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.event_binder import (
    input_event_bind,
    callback_event_bind,
)
from ratroyale.frontend.pages.page_managers.page_registry import register_page

from ratroyale.frontend.pages.page_elements.hitbox import RectangleHitbox


from ratroyale.frontend.pages.page_elements.element import ElementWrapper


from ratroyale.frontend.pages.page_elements.spatial_component import (
    SpatialComponent,
    Camera,
)
from ratroyale.frontend.visual.asset_management.spritesheet_manager import (
    SpritesheetManager,
)
from ratroyale.frontend.visual.asset_management.game_obj_to_sprite_registry import (
    SQUEAK_IMAGE_METADATA_REGISTRY,
)
from ratroyale.backend.entities.rodents.vanguard import TailBlazer


from ratroyale.frontend.visual.asset_management.visual_component import VisualComponent
from ratroyale.frontend.visual.asset_management.spritesheet_structure import (
    SpritesheetComponent,
)


@register_page
class SqueakOverlay(Page):
    def __init__(
        self, coordination_manager: CoordinationManager, camera: Camera
    ) -> None:
        super().__init__(coordination_manager, camera, is_blocking=False)
        self.CARD_GROUPING_NAME = "UI_CARD"
        self.selected_squeak: str | None = None

    def on_open(self) -> None:
        pass

    def define_initial_gui(self) -> list[ElementWrapper]:
        return []

    # region Input Bindings

    @callback_event_bind("start_game")
    def _start_game(self, msg: PageCallbackEvent[Board]) -> None:
        """Create card elements for players after receiving game board."""

        card_elements: list[ElementWrapper] = []

        CARD_WIDTH, CARD_HEIGHT = 143, 90
        CARD_SPACING = 10
        LEFT_MARGIN = 0
        TOP_MARGIN = 80

        sprite_metadata = SQUEAK_IMAGE_METADATA_REGISTRY[TailBlazer]
        cached_spritesheet_name = SpritesheetManager.register_spritesheet(
            sprite_metadata
        ).get_key()

        for i in range(5):
            card_rect = pygame.Rect(
                LEFT_MARGIN,
                TOP_MARGIN + i * (CARD_HEIGHT + CARD_SPACING),
                CARD_WIDTH,
                CARD_HEIGHT,
            )

            card_element = ElementWrapper(
                registered_name=f"card_{i}",  # Replace with Squeak ID?
                grouping_name=self.CARD_GROUPING_NAME,
                camera=self.camera,
                spatial_component=SpatialComponent(
                    card_rect,
                    space_mode="SCREEN",
                ),
                interactable_component=RectangleHitbox(),
                is_blocking=True,
                visual_component=VisualComponent(
                    SpritesheetComponent(spritesheet_reference=cached_spritesheet_name),
                    "NONE",
                ),
            )

            card_elements.append(card_element)

        self.setup_elements(card_elements)

    @input_event_bind("card", GestureType.CLICK.to_pygame_event())
    def squeak_clicked(self, msg: pygame.event.Event) -> None:
        squeak_id = get_id(msg)
        if squeak_id:
            self.selected_squeak = squeak_id

    @callback_event_bind("has_selected_squeak")
    def place_squeak(self, msg: pygame.event.Event) -> None:
        # send data back to game board to place new rodent element

        self.selected_squeak = None

    @input_event_bind("card", GestureType.DRAG_START.to_pygame_event())
    def squeak_drag_start(self, msg: pygame.event.Event) -> None:
        squeak_id = get_id(msg)
        gesture_data = get_gesture_data(msg)
        if squeak_id:
            squeak_element = self._element_manager.get_element_wrapper(
                squeak_id, self.CARD_GROUPING_NAME
            )

        if squeak_element and gesture_data.mouse_pos and squeak_id:
            squeak_element.spatial_component.center_to_screen_pos(
                gesture_data.mouse_pos, self.camera
            )
            self.selected_squeak = squeak_id

    @input_event_bind(None, GestureType.DRAG.to_pygame_event())
    def _on_drag(self, msg: pygame.event.Event) -> None:
        if self.selected_squeak is None:
            return

        element_id = self.selected_squeak
        entity = self._element_manager.get_element_wrapper(
            element_id, self.CARD_GROUPING_NAME
        )
        gesture_data = get_gesture_data(msg)

        if entity and gesture_data.mouse_pos:
            entity.spatial_component.set_position(gesture_data.mouse_pos)

    @input_event_bind("card", GestureType.DRAG_END.to_pygame_event())
    def _on_drag_end(self, msg: pygame.event.Event) -> None:
        self.selected_squeak = None
        self.camera.end_drag()
