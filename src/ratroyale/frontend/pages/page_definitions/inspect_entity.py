import pygame
import pygame_gui

from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.input_token import InputManagerEvent
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *

from ratroyale.frontend.gesture.gesture_data import GestureType

from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.event_binder import input_event_bind
from ratroyale.frontend.pages.page_managers.page_registry import register_page

from ratroyale.frontend.pages.page_elements.element import ElementWrapper, ui_element_wrapper
from ratroyale.frontend.pages.page_elements.spatial_component import Camera


@register_page
class InspectEntity(Page):
    def __init__(self, coordination_manager: "CoordinationManager", camera: Camera) -> None:
        super().__init__(coordination_manager, is_blocking=False, theme_name="inspect_entity", camera=camera)

    def define_initial_gui(self) -> list[ElementWrapper]:
        elements: list[ElementWrapper] = []

        panel = ui_element_wrapper(
            pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect(10, 60, 300, 420),
                manager=self.gui_manager,
                object_id=pygame_gui.core.ObjectID(class_id="InspectPanel", object_id="inspect_panel"),
            ),
            registered_name="inspect_panel",
            grouping_name="inspect_entity",
            camera=self.camera,
        )
        elements.append(panel)

        portrait_area = ui_element_wrapper(
            pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect(10, 10, 120, 120),
                manager=self.gui_manager,
                container=panel.get_interactable(pygame_gui.elements.UIPanel),
                object_id=pygame_gui.core.ObjectID(class_id="PortraitArea", object_id="portrait_area"),
            ),
            registered_name="portrait_area",
            grouping_name="inspect_entity",
            camera=self.camera,
        )
        elements.append(portrait_area)

        rat_name = ui_element_wrapper(
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(140, 10, 140, 30),
                text="Rat Name",
                manager=self.gui_manager,
                container=panel.get_interactable(pygame_gui.elements.UIPanel),
                object_id=pygame_gui.core.ObjectID(class_id="InspectLabel", object_id="rat_name"),
            ),
            registered_name="rat_name",
            grouping_name="inspect_entity",
            camera=self.camera,
        )
        elements.append(rat_name)

        description = ui_element_wrapper(
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(10, 140, 280, 80),
                text="Description goes here",
                manager=self.gui_manager,
                container=panel.get_interactable(pygame_gui.elements.UIPanel),
                object_id=pygame_gui.core.ObjectID(class_id="InspectLabel", object_id="description"),
            ),
            registered_name="description",
            grouping_name="inspect_entity",
            camera=self.camera,
        )
        elements.append(description)

        return elements

