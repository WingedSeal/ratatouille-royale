from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *


from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.event_binder import input_event_bind
from ratroyale.frontend.pages.page_managers.page_registry import register_page
from ratroyale.frontend.pages.page_elements.spatial_component import (
    Camera,
)
from ratroyale.frontend.pages.page_elements.element import (
    ElementWrapper,
    ui_element_wrapper,
)
from ratroyale.frontend.visual.screen_constants import SCREEN_SIZE_HALVED

import pygame_gui
import pygame


@register_page
class SelectTargetPromptPage(Page):
    def __init__(
        self, coordination_manager: CoordinationManager, camera: Camera
    ) -> None:
        super().__init__(coordination_manager, camera, is_blocking=False)

    def define_initial_gui(self) -> list[ElementWrapper]:
        """Return all GUI elements for the TestPage."""
        gui_elements: list[ElementWrapper] = []

        btn_width = 80
        btn_height = 40
        btn_x = SCREEN_SIZE_HALVED[0] - btn_width / 2
        btn_y = 100

        # Nested button inside the panel
        cancel_skill_button = ui_element_wrapper(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(btn_x, btn_y, btn_width, btn_height),
                text="Cancel",
                manager=self.gui_manager,
                object_id=pygame_gui.core.ObjectID(
                    class_id="CancelSkillButton", object_id="cancel_skill_button"
                ),
            ),
            registered_name="cancel_skill_button",
            camera=self.camera,
        )
        gui_elements.append(cancel_skill_button)
        # endregion

        return gui_elements

    @input_event_bind("cancel_skill_button", pygame_gui.UI_BUTTON_PRESSED)
    def close_panel(self, msg: pygame.event.Event) -> None:
        self.close_self()
        self.post(PageCallbackEvent("skill_canceled"))
        self.post(GameManagerEvent("skill_canceled"))
