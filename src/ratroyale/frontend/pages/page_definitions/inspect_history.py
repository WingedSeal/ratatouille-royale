from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.input_token import InputManagerEvent
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *

from ratroyale.frontend.gesture.gesture_data import GestureType

from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.event_binder import input_event_bind
from ratroyale.frontend.pages.page_managers.page_registry import register_page

from ratroyale.frontend.pages.page_elements.element_builder import (
    ElementConfig,
    UIRegisterForm,
)

import pygame
import pygame_gui

@register_page
class InspectHistory(Page):
    def __init__(self, coordination_manager: "CoordinationManager") -> None:
        super().__init__(coordination_manager, is_blocking=True, theme_name="inspect_history")

    def define_initial_gui(self) -> list[UIRegisterForm]:
        gui_elements: list[UIRegisterForm] = []

        panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(150, 60, 500, 420),
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(class_id="InspectHistoryPanel", object_id="inspect_history_panel"),
        )
        gui_elements.append(UIRegisterForm("inspect_history_panel", panel))

        portrait_area = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(10, 10, 120, 120),
            manager=self.gui_manager,
            container=panel,
            object_id=pygame_gui.core.ObjectID(class_id="PortraitArea", object_id="history_portrait"),
        )
        gui_elements.append(UIRegisterForm("history_portrait", portrait_area))

        history_title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(140, 10, 350, 30),
            text="History Event",
            manager=self.gui_manager,
            container=panel,
            object_id=pygame_gui.core.ObjectID(class_id="InspectHistoryLabel", object_id="history_title"),
        )
        gui_elements.append(UIRegisterForm("history_title", history_title))

        history_desc = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(140, 44, 350, 86),
            text="Clanker moves from (xx, xx) to (xx, xx).",
            manager=self.gui_manager,
            container=panel,
            object_id=pygame_gui.core.ObjectID(class_id="InspectHistoryLabel", object_id="history_desc"),
        )
        gui_elements.append(UIRegisterForm("history_desc", history_desc))

        map_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(10, 140, 480, 260),
            manager=self.gui_manager,
            container=panel,
            object_id=pygame_gui.core.ObjectID(class_id="HistoryMap", object_id="history_map"),
        )
        gui_elements.append(UIRegisterForm("history_map", map_panel))

        exit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(410, 10, 80, 30),
            text="exit",
            manager=self.gui_manager,
            container=panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="InspectHistoryButton", object_id="exit_button"
            )
        )
        gui_elements.append(UIRegisterForm("exit_button", exit_button))

        return gui_elements
    
    @input_event_bind("exit_button", pygame_gui.UI_BUTTON_PRESSED)
    def on_exit_click(self, msg: pygame.event.Event) -> None:
        self.post(PageNavigationEvent(action_list=[(PageNavigation.CLOSE_TOP, None)]))

