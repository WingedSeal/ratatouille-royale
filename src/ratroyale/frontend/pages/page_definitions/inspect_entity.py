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

        stats_button = ui_element_wrapper(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(10, 230, 90, 36),
                text="Stats",
                manager=self.gui_manager,
                container=panel.get_interactable(pygame_gui.elements.UIPanel),
                object_id=pygame_gui.core.ObjectID(class_id="InspectButton", object_id="stats_button"),
            ),
            registered_name="stats_button",
            grouping_name="inspect_entity",
            camera=self.camera,
        )
        elements.append(stats_button)

        passive_button = ui_element_wrapper(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(105, 230, 90, 36),
                text="Passive",
                manager=self.gui_manager,
                container=panel.get_interactable(pygame_gui.elements.UIPanel),
                object_id=pygame_gui.core.ObjectID(class_id="InspectButton", object_id="passive_button"),
            ),
            registered_name="passive_button",
            grouping_name="inspect_entity",
            camera=self.camera,
        )
        elements.append(passive_button)

        lore_button = ui_element_wrapper(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(200, 230, 90, 36),
                text="LORE",
                manager=self.gui_manager,
                container=panel.get_interactable(pygame_gui.elements.UIPanel),
                object_id=pygame_gui.core.ObjectID(class_id="InspectButton", object_id="lore_button"),
            ),
            registered_name="lore_button",
            grouping_name="inspect_entity",
            camera=self.camera,
        )
        elements.append(lore_button)

        stats_panel = ui_element_wrapper(
            pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect(10, 276, 280, 120),
                manager=self.gui_manager,
                container=panel.get_interactable(pygame_gui.elements.UIPanel),
                object_id=pygame_gui.core.ObjectID(class_id="StatsPanel", object_id="stats_panel"),
            ),
            registered_name="stats_panel",
            grouping_name="inspect_entity",
            camera=self.camera,
        )
        elements.append(stats_panel)

        hp_label = ui_element_wrapper(
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(8, 6, 120, 24),
                text="HP: --",
                manager=self.gui_manager,
                container=stats_panel.get_interactable(pygame_gui.elements.UIPanel),
                object_id=pygame_gui.core.ObjectID(class_id="StatLabel", object_id="hp_label"),
            ),
            registered_name="hp_label",
            grouping_name="inspect_entity",
            camera=self.camera,
        )
        elements.append(hp_label)

        def_label = ui_element_wrapper(
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(8, 34, 120, 24),
                text="DEF: --",
                manager=self.gui_manager,
                container=stats_panel.get_interactable(pygame_gui.elements.UIPanel),
                object_id=pygame_gui.core.ObjectID(class_id="StatLabel", object_id="def_label"),
            ),
            registered_name="def_label",
            grouping_name="inspect_entity",
            camera=self.camera,
        )
        elements.append(def_label)

        speed_label = ui_element_wrapper(
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(140, 6, 120, 24),
                text="SPEED: --",
                manager=self.gui_manager,
                container=stats_panel.get_interactable(pygame_gui.elements.UIPanel),
                object_id=pygame_gui.core.ObjectID(class_id="StatLabel", object_id="speed_label"),
            ),
            registered_name="speed_label",
            grouping_name="inspect_entity",
            camera=self.camera,
        )
        elements.append(speed_label)

        stam_label = ui_element_wrapper(
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(140, 34, 120, 24),
                text="STAMINA: --",
                manager=self.gui_manager,
                container=stats_panel.get_interactable(pygame_gui.elements.UIPanel),
                object_id=pygame_gui.core.ObjectID(class_id="StatLabel", object_id="stam_label"),
            ),
            registered_name="stam_label",
            grouping_name="inspect_entity",
            camera=self.camera,
        )
        elements.append(stam_label)

        skill_panel = ui_element_wrapper(
            pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect(320, 60, 300, 420),
                manager=self.gui_manager,
                object_id=pygame_gui.core.ObjectID(class_id="SkillInspectPanel", object_id="skill_panel"),
            ),
            registered_name="skill_panel",
            grouping_name="inspect_entity",
            camera=self.camera,
        )
        elements.append(skill_panel)

        skill_name = ui_element_wrapper(
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(8, 8, 284, 28),
                text="Skill Name",
                manager=self.gui_manager,
                container=skill_panel.get_interactable(pygame_gui.elements.UIPanel),
                object_id=pygame_gui.core.ObjectID(class_id="SkillLabel", object_id="skill_name"),
            ),
            registered_name="skill_name",
            grouping_name="inspect_entity",
            camera=self.camera,
        )
        elements.append(skill_name)

        skill_desc = ui_element_wrapper(
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(8, 44, 284, 120),
                text="Skill description goes here",
                manager=self.gui_manager,
                container=skill_panel.get_interactable(pygame_gui.elements.UIPanel),
                object_id=pygame_gui.core.ObjectID(class_id="SkillLabel", object_id="skill_desc"),
            ),
            registered_name="skill_desc",
            grouping_name="inspect_entity",
            camera=self.camera,
        )
        elements.append(skill_desc)

        return elements

