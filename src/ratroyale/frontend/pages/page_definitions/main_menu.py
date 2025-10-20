import pygame
import pygame_gui

from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.visual_token import *
from ratroyale.frontend.pages.page_managers.event_binder import input_event_bind
from ratroyale.frontend.pages.page_managers.page_registry import register_page
from ratroyale.frontend.gesture.gesture_data import GestureType

from ratroyale.frontend.pages.page_elements.element import (
    ElementWrapper,
    ui_element_wrapper,
)
from ratroyale.frontend.pages.page_elements.spatial_component import (
    SpatialComponent,
    Camera,
)
from ratroyale.frontend.visual.asset_management.visual_component import VisualComponent
from ratroyale.frontend.visual.anim.core.transform_anim import ScaleAnim
from ratroyale.frontend.visual.asset_management.game_obj_to_sprite_registry import (
    SPRITE_METADATA_REGISTRY,
)
from ratroyale.frontend.visual.asset_management.spritesheet_manager import (
    SpritesheetManager,
)

from ratroyale.frontend.pages.page_elements.hitbox import RectangleHitbox

from ratroyale.backend.entities.rodents.vanguard import TailBlazer

from ratroyale.frontend.visual.asset_management.spritesheet_structure import (
    SpritesheetComponent,
)
from ratroyale.frontend.visual.anim.core.anim_settings import (
    ScaleMode,
    TimingMode,
    VerticalAnchor,
    HorizontalAnchor,
)

from ..page_managers.base_page import Page

import pytweening  # type: ignore


# TODO: make helpers to make button registration easier
@register_page
class MainMenu(Page):
    def __init__(
        self, coordination_manager: CoordinationManager, camera: Camera
    ) -> None:
        super().__init__(coordination_manager, theme_name="main_menu", camera=camera)

    def define_initial_gui(self) -> list[ElementWrapper]:
        """Return all GUI elements for the main menu page."""

        elements: list[ElementWrapper] = []

        start_button_id = "start_button"
        start_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(100, 100, 200, 50),
            text="Start",
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="MainMenuButton", object_id=start_button_id
            ),
        )
        start_button_element = ui_element_wrapper(
            start_button, start_button_id, self.camera
        )
        elements.append(start_button_element)

        # Quit button
        quit_button_id = "quit_button"
        quit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(100, 200, 200, 50),
            text="Quit",
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="MainMenuButton", object_id=quit_button_id
            ),
        )
        quit_button_element = ui_element_wrapper(
            quit_button, quit_button_id, self.camera
        )
        elements.append(quit_button_element)

        # GUI Demo button
        gui_demo_button_id = "gui_demo_button"
        gui_demo_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(100, 300, 200, 50),
            text="Go to GUI demo",
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="MainMenuButton", object_id=gui_demo_button_id
            ),
        )
        gui_demo_element = ui_element_wrapper(
            gui_demo_button, gui_demo_button_id, self.camera
        )
        elements.append(gui_demo_element)

        # Element Demo button
        element_demo_button_id = "element_demo_button"
        element_demo_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(400, 300, 200, 50),
            text="Go to Element demo",
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="MainMenuButton", object_id=element_demo_button_id
            ),
        )
        element_demo_element = ui_element_wrapper(
            element_demo_button, element_demo_button_id, self.camera
        )
        elements.append(element_demo_element)

        # Get testing sprite
        sprite_metadata = SPRITE_METADATA_REGISTRY[TailBlazer]
        cached_spritesheet_name = SpritesheetManager.register_spritesheet(
            sprite_metadata
        ).get_key()

        test_names = [f"entity_test_{i}" for i in range(1, 4)]
        test_coords = [
            pygame.Rect(100, 100, 80, 80),
            pygame.Rect(100, 150, 80, 80),
            pygame.Rect(-50, -25, 80, 80),
        ]

        for name, coords in zip(test_names, test_coords):
            tailblazer = ElementWrapper(
                registered_name=name,
                grouping_name="RODENT",
                camera=self.camera,
                spatial_component=SpatialComponent(
                    local_rect=pygame.Rect(coords), space_mode="WORLD"
                ),
                interactable_component=RectangleHitbox(),
                visual_component=VisualComponent(
                    SpritesheetComponent(spritesheet_reference=cached_spritesheet_name),
                    starting_anim="IDLE",
                ),
            )
            elements.append(tailblazer)

        return elements

    # region Input Responses

    @input_event_bind("start_button", pygame_gui.UI_BUTTON_PRESSED)
    def on_start_click(self, msg: pygame.event.Event) -> None:
        self.coordination_manager.put_message(
            PageNavigationEvent(
                action_list=[
                    (PageNavigation.CLOSE_ALL, None),
                    (PageNavigation.OPEN, "GameBoard"),
                    (PageNavigation.OPEN, "PauseButton"),
                    (PageNavigation.OPEN, "EntityList"),
                    (PageNavigation.OPEN, "GameInfoPage"),
                ]
            )
        )

    @input_event_bind("quit_button", pygame_gui.UI_BUTTON_PRESSED)
    def _on_quit_click(self, msg: pygame.event.Event) -> None:
        self.coordination_manager.stop_game()

    @input_event_bind("gui_demo_button", pygame_gui.UI_BUTTON_PRESSED)
    def _on_gui_demo_click(self, msg: pygame.event.Event) -> None:
        self.post(
            PageNavigationEvent(
                action_list=[
                    (PageNavigation.CLOSE_ALL, None),
                    (PageNavigation.OPEN, "GUIDemo"),
                ]
            )
        )

    @input_event_bind("element_demo_button", pygame_gui.UI_BUTTON_PRESSED)
    def _on_element_demo_click(self, msg: pygame.event.Event) -> None:
        element_wrapper = self._element_manager.get_element_wrapper(
            "entity_test_1", "RODENT"
        )
        vis = element_wrapper.visual_component
        if vis:
            scale_anim = ScaleAnim(
                easing_func=pytweening.easeOutCirc,
                timing_mode=TimingMode.DURATION_PER_LOOP,
                period_in_seconds=1,  # duration of one loop in seconds
                reverse_pass_per_loop=True,  # whether to reverse direction at the end of each loop
                run_together_with_default=True,  # optional, depends on your AnimEvent logic
                callback=None,  # optional callback name or None
                loop_count=5,  # number of loops (None = infinite)
                spatial_component=element_wrapper.spatial_component,
                camera=self.camera,
                align_hitbox_during_anim=False,
                scale_mode=ScaleMode.SCALE_BY_FACTOR,
                target=(0.8, 1.2),
                expansion_anchor=(VerticalAnchor.LOWER, HorizontalAnchor.MIDDLE),
            )

            # move_anim = MoveAnim(
            #     easing_func=pytweening.easeOutBack,
            #     timing_mode="DURATION_PER_LOOP",  # or "DURATION_IN_TOTAL"
            #     period=1.0,  # duration of one loop in seconds
            #     reverse_pass_per_loop=True,  # whether to reverse direction at the end of each loop
            #     compose_with_default=True,  # optional, depends on your AnimEvent logic
            #     callback=None,  # optional callback name or None
            #     loop_count=5,  # number of loops (None = infinite)
            #     spatial_component=element_wrapper.spatial_component,
            #     camera=self.camera,
            #     align_hitbox_during_anim=False,
            #     move_mode="MOVE_BY",
            #     direction_vector=(100, 100),
            # )

            # assert vis.spritesheet_component
            # sprite_anim = SpriteAnim(
            #     spritesheet_component=vis.spritesheet_component,
            #     period=1,
            #     reverse_pass_per_loop=True,
            #     loop_count=5,
            #     animation_name="DIE",
            #     timing_mode="DURATION_PER_LOOP",
            # )
            vis.queue_override_animation(scale_anim)

    @input_event_bind("entity_test_2", GestureType.CLICK.to_pygame_event())
    def click_test(self, msg: pygame.event.Event) -> None:
        print("entity clicked")
        self.camera.zoom_at(self.camera.scale + 0.1)

    # endregion
