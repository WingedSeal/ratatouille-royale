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

        # region Panel + nested button
        select_target_panel_id = "select_target_panel"
        select_target_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(200, 100, 400, 100),
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="SelectTargetPanel", object_id="select_target_panel"
            ),
        )
        select_target_panel_element = ui_element_wrapper(
            select_target_panel, select_target_panel_id, self.camera
        )
        gui_elements.append(select_target_panel_element)

        # Nested button inside the panel
        pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(300, 10, 90, 70),
            text="Cancel Skill",
            manager=self.gui_manager,
            container=select_target_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="CancelSkillButton", object_id="cancel_skill_button"
            ),
        )
        # endregion

        return gui_elements

    @input_event_bind("cancel_skill_button", pygame_gui.UI_BUTTON_PRESSED)
    def close_panel(self, msg: pygame.event.Event) -> None:
        CoordinationManager.put_message(
            PageNavigationEvent(
                action_list=[
                    (PageNavigation.CLOSE, "SelectTargetPromptPage"),
                ]
            )
        )
        CoordinationManager.put_message(PageCallbackEvent("skill_canceled"))
        CoordinationManager.put_message(GameManagerEvent("skill_canceled"))
