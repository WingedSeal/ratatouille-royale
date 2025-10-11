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
class InspectEntity(Page):
    def __init__(self, coordination_manager: "CoordinationManager") -> None:
        super().__init__(coordination_manager, is_blocking=False, theme_name="inspect_entity")

    def define_initial_gui(self) -> list[UIRegisterForm]:
        gui_elements: list[UIRegisterForm] = []

        panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(10, 60, 300, 420),
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(class_id="InspectPanel", object_id="inspect_panel"),
        )
        gui_elements.append(UIRegisterForm("inspect_panel", panel))

        portrait_area = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(10, 10, 120, 120),
            manager=self.gui_manager,
            container=panel,
            object_id=pygame_gui.core.ObjectID(class_id="PortraitArea", object_id="portrait_area"),
        )
        gui_elements.append(UIRegisterForm("portrait_area", portrait_area))

        rat_name = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(140, 10, 140, 30),
            text="Rat Name",
            manager=self.gui_manager,
            container=panel,
            object_id=pygame_gui.core.ObjectID(class_id="InspectLabel", object_id="rat_name"),
        )
        gui_elements.append(UIRegisterForm("rat_name", rat_name))

        description = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 140, 280, 80),
            text="Description goes here",
            manager=self.gui_manager,
            container=panel,
            object_id=pygame_gui.core.ObjectID(class_id="InspectLabel", object_id="description"),
        )
        gui_elements.append(UIRegisterForm("description", description))

        stats_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 230, 90, 36),
            text="Stats",
            manager=self.gui_manager,
            container=panel,
            object_id=pygame_gui.core.ObjectID(class_id="InspectButton", object_id="stats_button"),
        )
        gui_elements.append(UIRegisterForm("stats_button", stats_button))

        passive_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(105, 230, 90, 36),
            text="Passive",
            manager=self.gui_manager,
            container=panel,
            object_id=pygame_gui.core.ObjectID(class_id="InspectButton", object_id="passive_button"),
        )
        gui_elements.append(UIRegisterForm("passive_button", passive_button))

        lore_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(200, 230, 90, 36),
            text="LORE",
            manager=self.gui_manager,
            container=panel,
            object_id=pygame_gui.core.ObjectID(class_id="InspectButton", object_id="lore_button"),
        )
        gui_elements.append(UIRegisterForm("lore_button", lore_button))

        stats_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(10, 276, 280, 120),
            manager=self.gui_manager,
            container=panel,
            object_id=pygame_gui.core.ObjectID(class_id="StatsPanel", object_id="stats_panel"),
        )
        gui_elements.append(UIRegisterForm("stats_panel", stats_panel))

        hp_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(8, 6, 120, 24),
            text="HP: --",
            manager=self.gui_manager,
            container=stats_panel,
            object_id=pygame_gui.core.ObjectID(class_id="StatLabel", object_id="hp_label"),
        )
        gui_elements.append(UIRegisterForm("hp_label", hp_label))

        def_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(8, 34, 120, 24),
            text="DEF: --",
            manager=self.gui_manager,
            container=stats_panel,
            object_id=pygame_gui.core.ObjectID(class_id="StatLabel", object_id="def_label"),
        )
        gui_elements.append(UIRegisterForm("def_label", def_label))

        speed_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(140, 6, 120, 24),
            text="SPEED: --",
            manager=self.gui_manager,
            container=stats_panel,
            object_id=pygame_gui.core.ObjectID(class_id="StatLabel", object_id="speed_label"),
        )
        gui_elements.append(UIRegisterForm("speed_label", speed_label))

        stam_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(140, 34, 120, 24),
            text="STAMINA: --",
            manager=self.gui_manager,
            container=stats_panel,
            object_id=pygame_gui.core.ObjectID(class_id="StatLabel", object_id="stam_label"),
        )
        gui_elements.append(UIRegisterForm("stam_label", stam_label))

        skill_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(320, 60, 300, 420),
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(class_id="SkillInspectPanel", object_id="skill_panel"),
        )
        gui_elements.append(UIRegisterForm("skill_panel", skill_panel))

        skill_name = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(8, 8, 284, 28),
            text="Skill Name",
            manager=self.gui_manager,
            container=skill_panel,
            object_id=pygame_gui.core.ObjectID(class_id="SkillLabel", object_id="skill_name"),
        )
        gui_elements.append(UIRegisterForm("skill_name", skill_name))

        skill_desc = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(8, 44, 284, 120),
            text="Skill description goes here",
            manager=self.gui_manager,
            container=skill_panel,
            object_id=pygame_gui.core.ObjectID(class_id="SkillLabel", object_id="skill_desc"),
        )
        gui_elements.append(UIRegisterForm("skill_desc", skill_desc))

        return gui_elements

