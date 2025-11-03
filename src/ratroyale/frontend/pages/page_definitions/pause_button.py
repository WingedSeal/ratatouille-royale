import pygame
import pygame_gui

from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.visual_token import *
from ratroyale.frontend.pages.page_managers.event_binder import input_event_bind
from ratroyale.frontend.pages.page_managers.page_registry import register_page

from ratroyale.frontend.pages.page_elements.element import (
    ElementWrapper,
    ui_element_wrapper,
)
from ratroyale.frontend.pages.page_elements.spatial_component import Camera
from ratroyale.frontend.visual.screen_constants import SCREEN_SIZE

from ..page_managers.base_page import Page


@register_page
class PauseButton(Page):
    def __init__(
        self, coordination_manager: CoordinationManager, camera: Camera
    ) -> None:
        super().__init__(
            coordination_manager,
            is_blocking=False,
            theme_name="pause_button",
            camera=camera,
        )

    def define_initial_gui(self) -> list[ElementWrapper]:
        elements: list[ElementWrapper] = []

        pause_button_pos = (SCREEN_SIZE[0] * 7 / 8, 0)
        pause_button_dim = (SCREEN_SIZE[0] / 8, SCREEN_SIZE[1] / 12)
        pause_button = ui_element_wrapper(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(
                    pause_button_pos[0],
                    pause_button_pos[1],
                    pause_button_dim[0],
                    pause_button_dim[1],
                ),
                text="Pause",
                manager=self.gui_manager,
                object_id=pygame_gui.core.ObjectID(
                    class_id="PauseButton", object_id="pause_button"
                ),
            ),
            registered_name="pause_button",
            grouping_name="pause_button",
            camera=self.camera,
        )
        elements.append(pause_button)

        return elements

    # --- Input Responses ---
    @input_event_bind("pause_button", pygame_gui.UI_BUTTON_PRESSED)
    def on_pause_click(self, msg: pygame.event.Event) -> None:
        self.post(PageNavigationEvent(action_list=[(PageNavigation.OPEN, "PauseMenu")]))
