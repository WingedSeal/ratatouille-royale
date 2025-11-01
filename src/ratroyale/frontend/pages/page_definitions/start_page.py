from ratroyale.coordination_manager import CoordinationManager

from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *


from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.page_registry import register_page
from ratroyale.frontend.pages.page_managers.event_binder import input_event_bind

from ratroyale.frontend.pages.page_elements.element import (
    ElementWrapper,
)
from ..page_elements.spatial_component import Camera

import pygame_gui
import pygame


@register_page
class StartPage(Page):
    def __init__(
        self, coordination_manager: CoordinationManager, camera: Camera
    ) -> None:
        super().__init__(coordination_manager, camera)

    def define_initial_gui(self) -> list[ElementWrapper]:
        gui_elements: list[ElementWrapper] = []

        # === Start button ===
        pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, -180, 150, 60),
            text="Start",
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="StartButton", object_id="start_button"
            ),
            anchors={"centerx": "centerx", "bottom": "bottom"},
        )
        return gui_elements

    @input_event_bind("start_button", pygame_gui.UI_BUTTON_PRESSED)
    def proceed_to_select_profile(self, msg: pygame.event.Event) -> None:
        CoordinationManager.put_message(
            PageNavigationEvent(
                [
                    (PageNavigation.CLOSE, "StartPage"),
                    (PageNavigation.OPEN, "PlayerProfile"),
                ]
            )
        )
