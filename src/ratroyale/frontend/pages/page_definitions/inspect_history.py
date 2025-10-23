import pygame
import pygame_gui

from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *


from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.event_binder import input_event_bind
from ratroyale.frontend.pages.page_managers.page_registry import register_page

from ratroyale.frontend.pages.page_elements.element import (
    ElementWrapper,
    ui_element_wrapper,
)
from ratroyale.frontend.pages.page_elements.spatial_component import Camera


@register_page
class InspectHistory(Page):
    def __init__(
        self, coordination_manager: "CoordinationManager", camera: Camera
    ) -> None:
        super().__init__(
            coordination_manager,
            is_blocking=True,
            theme_name="inspect_history",
            camera=camera,
        )

    def define_initial_gui(self) -> list[ElementWrapper]:
        elements: list[ElementWrapper] = []

        panel = ui_element_wrapper(
            pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect(150, 60, 500, 420),
                manager=self.gui_manager,
                object_id=pygame_gui.core.ObjectID(
                    class_id="InspectHistoryPanel", object_id="inspect_history_panel"
                ),
            ),
            registered_name="inspect_history_panel",
            grouping_name="inspect_history",
            camera=self.camera,
        )
        elements.append(panel)

        portrait_area = ui_element_wrapper(
            pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect(10, 10, 120, 120),
                manager=self.gui_manager,
                container=panel.get_interactable(pygame_gui.elements.UIPanel),
                object_id=pygame_gui.core.ObjectID(
                    class_id="PortraitArea", object_id="history_portrait"
                ),
            ),
            registered_name="history_portrait",
            grouping_name="inspect_history",
            camera=self.camera,
        )
        elements.append(portrait_area)

        history_title = ui_element_wrapper(
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(140, 10, 350, 30),
                text="History Event",
                manager=self.gui_manager,
                container=panel.get_interactable(pygame_gui.elements.UIPanel),
                object_id=pygame_gui.core.ObjectID(
                    class_id="InspectHistoryLabel", object_id="history_title"
                ),
            ),
            registered_name="history_title",
            grouping_name="inspect_history",
            camera=self.camera,
        )
        elements.append(history_title)

        history_desc = ui_element_wrapper(
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(140, 44, 350, 86),
                text="Clanker moves from (xx, xx) to (xx, xx).",
                manager=self.gui_manager,
                container=panel.get_interactable(pygame_gui.elements.UIPanel),
                object_id=pygame_gui.core.ObjectID(
                    class_id="InspectHistoryLabel", object_id="history_desc"
                ),
            ),
            registered_name="history_desc",
            grouping_name="inspect_history",
            camera=self.camera,
        )
        elements.append(history_desc)

        map_panel = ui_element_wrapper(
            pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect(10, 140, 480, 260),
                manager=self.gui_manager,
                container=panel.get_interactable(pygame_gui.elements.UIPanel),
                object_id=pygame_gui.core.ObjectID(
                    class_id="HistoryMap", object_id="history_map"
                ),
            ),
            registered_name="history_map",
            grouping_name="inspect_history",
            camera=self.camera,
        )
        elements.append(map_panel)

        exit_button = ui_element_wrapper(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(410, 10, 80, 30),
                text="exit",
                manager=self.gui_manager,
                container=panel.get_interactable(pygame_gui.elements.UIPanel),
                object_id=pygame_gui.core.ObjectID(
                    class_id="InspectHistoryButton", object_id="exit_button"
                ),
            ),
            registered_name="exit_button",
            grouping_name="inspect_history",
            camera=self.camera,
        )
        elements.append(exit_button)

        return elements

    @input_event_bind("exit_button", pygame_gui.UI_BUTTON_PRESSED)
    def on_exit_click(self, msg: pygame.event.Event) -> None:
        self.post(PageNavigationEvent(action_list=[(PageNavigation.CLOSE_TOP, None)]))

    # @input_event_bind(None, GestureType.CLICK.to_pygame_event())
    # def on_click_outside(self, msg: pygame.event.Event) -> None:
    #     if hasattr(msg, "ui_element"):
    #         return

    #     panel = self._element_manager.get_element("inspect_history_panel")

    #     if panel and hasattr(msg, "pos"):
    #         click_pos = msg.pos
    #         panel_rect = panel.spatial_component.get_screen_rect(self.camera)

    #         if not panel_rect.collidepoint(click_pos):
    #             self.post(
    #                 PageNavigationEvent(action_list=[(PageNavigation.CLOSE_TOP, None)])
    #             )
