import pygame
import pygame_gui

from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *

from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.event_binder import (
    input_event_bind,
    callback_event_bind,
)
from ratroyale.event_tokens.input_token import get_id, get_payload_from_msg
from ratroyale.frontend.pages.page_managers.page_registry import register_page

from ratroyale.frontend.pages.page_elements.element import (
    ElementWrapper,
    ui_element_wrapper,
)
from ratroyale.frontend.pages.page_elements.spatial_component import Camera
from ratroyale.event_tokens.payloads import (
    EntityPayload,
    CrumbUpdatePayload,
    SkillActivationPayload,
    IntegerPayload,
)
from ratroyale.backend.entities.rodent import Rodent

import uuid


@register_page
class InspectEntity(Page):
    def __init__(
        self, coordination_manager: "CoordinationManager", camera: Camera
    ) -> None:
        super().__init__(
            coordination_manager,
            is_blocking=True,
            theme_name="inspect_entity",
            camera=camera,
        )
        self.temp_skill_panel_id: str | None = None
        self.crumb: int = 0

    def define_initial_gui(self) -> list[ElementWrapper]:
        elements: list[ElementWrapper] = []

        return elements

    @input_event_bind("close_button", pygame_gui.UI_BUTTON_PRESSED)
    def close_button(self, msg: PageCallbackEvent) -> None:
        self.close_self()

    @callback_event_bind("entity_data")
    def show_entity_data(self, msg: PageCallbackEvent) -> None:
        payload = get_payload_from_msg(msg, EntityPayload)
        assert payload
        self.entity = payload.entity
        entity = self.entity
        elements: list[ElementWrapper] = []
        panel = ui_element_wrapper(
            pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect(10, 60, 300, 420),
                manager=self.gui_manager,
                object_id=pygame_gui.core.ObjectID(
                    class_id="InspectPanel", object_id="inspect_panel"
                ),
            ),
            registered_name="inspect_panel",
            grouping_name="inspect_entity",
            camera=self.camera,
        )
        elements.append(panel)

        close_button = ui_element_wrapper(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(
                    -40, 10, 30, 30
                ),  # offset from the top-right corner
                text="X",
                manager=self.gui_manager,
                container=panel.get_interactable(pygame_gui.elements.UIPanel),
                object_id=pygame_gui.core.ObjectID(
                    class_id="CloseButton", object_id="close_button"
                ),
                anchors={
                    "left": "right",  # position rect's left relative to parent's right
                },
            ),
            registered_name="close_button",
            grouping_name="close_button",
            camera=self.camera,
        )
        elements.append(close_button)

        portrait_area = ui_element_wrapper(
            pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect(10, 10, 120, 120),
                manager=self.gui_manager,
                container=panel.get_interactable(pygame_gui.elements.UIPanel),
                object_id=pygame_gui.core.ObjectID(
                    class_id="PortraitArea", object_id="portrait_area"
                ),
            ),
            registered_name="portrait_area",
            grouping_name="inspect_entity",
            camera=self.camera,
        )
        elements.append(portrait_area)

        rat_name = ui_element_wrapper(
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(140, 10, 140, 30),
                text=entity.name,
                manager=self.gui_manager,
                container=panel.get_interactable(pygame_gui.elements.UIPanel),
                object_id=pygame_gui.core.ObjectID(
                    class_id="InspectLabel", object_id="rat_name"
                ),
            ),
            registered_name="rat_name",
            grouping_name="inspect_entity",
            camera=self.camera,
        )
        elements.append(rat_name)

        description = ui_element_wrapper(
            pygame_gui.elements.UITextBox(
                relative_rect=pygame.Rect(10, 140, 280, 80),
                html_text=entity.description,
                manager=self.gui_manager,
                container=panel.get_interactable(pygame_gui.elements.UIPanel),
                object_id=pygame_gui.core.ObjectID(
                    class_id="InspectLabel", object_id="description"
                ),
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
                object_id=pygame_gui.core.ObjectID(
                    class_id="InspectButton", object_id="stats_button"
                ),
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
                object_id=pygame_gui.core.ObjectID(
                    class_id="InspectButton", object_id="passive_button"
                ),
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
                object_id=pygame_gui.core.ObjectID(
                    class_id="InspectButton", object_id="lore_button"
                ),
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
                object_id=pygame_gui.core.ObjectID(
                    class_id="StatsPanel", object_id="stats_panel"
                ),
            ),
            registered_name="stats_panel",
            grouping_name="inspect_entity",
            camera=self.camera,
        )
        elements.append(stats_panel)

        hp_label = ui_element_wrapper(
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(8, 6, 120, 24),
                text=f"HP: {entity.health} / {entity.max_health}",
                manager=self.gui_manager,
                container=stats_panel.get_interactable(pygame_gui.elements.UIPanel),
                object_id=pygame_gui.core.ObjectID(
                    class_id="StatLabel", object_id="hp_label"
                ),
            ),
            registered_name="hp_label",
            grouping_name="inspect_entity",
            camera=self.camera,
        )
        elements.append(hp_label)

        def_label = ui_element_wrapper(
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(8, 34, 120, 24),
                text=f"DEF: {entity.defense}",
                manager=self.gui_manager,
                container=stats_panel.get_interactable(pygame_gui.elements.UIPanel),
                object_id=pygame_gui.core.ObjectID(
                    class_id="StatLabel", object_id="def_label"
                ),
            ),
            registered_name="def_label",
            grouping_name="inspect_entity",
            camera=self.camera,
        )
        elements.append(def_label)

        # Only rodents have speed and stamina.
        # If the entity is not a rodent, we skip this part.
        if isinstance(entity, Rodent):
            speed_label = ui_element_wrapper(
                pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect(140, 6, 120, 24),
                    text=f"SPEED: {entity.speed}",
                    manager=self.gui_manager,
                    container=stats_panel.get_interactable(pygame_gui.elements.UIPanel),
                    object_id=pygame_gui.core.ObjectID(
                        class_id="StatLabel", object_id="speed_label"
                    ),
                ),
                registered_name="speed_label",
                grouping_name="inspect_entity",
                camera=self.camera,
            )
            elements.append(speed_label)

            stam_label = ui_element_wrapper(
                pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect(140, 34, 120, 24),
                    text=f"STAMINA: {entity.move_stamina} / {entity.max_move_stamina}",
                    manager=self.gui_manager,
                    container=stats_panel.get_interactable(pygame_gui.elements.UIPanel),
                    object_id=pygame_gui.core.ObjectID(
                        class_id="StatLabel", object_id="stam_label"
                    ),
                ),
                registered_name="stam_label",
                grouping_name="inspect_entity",
                camera=self.camera,
            )
            elements.append(stam_label)

        self.post(
            PageCallbackEvent(
                "can_show_skill_panel_or_not", payload=EntityPayload(self.entity)
            )
        )

        self.setup_elements(elements)

    @callback_event_bind("crumb")
    def set_crumb(self, msg: PageCallbackEvent) -> None:
        payload = get_payload_from_msg(msg, CrumbUpdatePayload)
        assert payload
        self.crumb = payload.new_crumb_amount

    @input_event_bind("skill", pygame_gui.UI_BUTTON_PRESSED)
    def activate_skill(self, msg: pygame.event.Event) -> None:
        # Get skill's ID and desc
        id = get_id(msg)
        assert id

        skill_button_name = self.get_leaf_object_id(id)
        assert skill_button_name
        skill_cost = self._element_manager.get_element(skill_button_name).get_payload(
            IntegerPayload
        )

        if skill_cost.value > self.crumb:
            return

        skill_id = int(id.split("_")[-1])

        ability_payload = SkillActivationPayload(skill_id, self.entity)
        self.close_self()
        self.post(
            PageNavigationEvent(
                [
                    (PageNavigation.OPEN, "SelectTargetPromptPage"),
                ]
            )
        )
        self.post(GameManagerEvent("ability_activation", ability_payload))

    @input_event_bind("skill", pygame_gui.UI_BUTTON_ON_UNHOVERED)
    def close_skill_description(self, msg: pygame.event.Event) -> None:
        if self.temp_skill_panel_id:
            self._element_manager.remove_element(self.temp_skill_panel_id)
            self.temp_skill_panel_id = None

    @input_event_bind("skill", pygame_gui.UI_BUTTON_ON_HOVERED)
    def show_skill_description(self, msg: pygame.event.Event) -> None:
        # Clear old skill desc panel in case the unhovered event never got emitted
        if self.temp_skill_panel_id:
            self._element_manager.remove_element(self.temp_skill_panel_id)
            self.temp_skill_panel_id = None

        # Get skill's ID and desc
        id = get_id(msg)
        assert id
        skill_id = int(id.split("_")[-1])
        skill = self.entity.skills[skill_id]
        assert isinstance(self.entity, Rodent)
        skill_name = skill.name
        skill_desc = self.entity.skill_descriptions()[skill_id]

        if skill_id == -1:
            skill_name = "Move"
            skill_desc = "Use crumbs to perform a movement."

        elements = []
        skill_panel_id = f"skill_panel_{uuid.uuid4()}"
        skill_panel = ui_element_wrapper(
            pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect(10, 60, 300, 420),
                manager=self.gui_manager,
                object_id=pygame_gui.core.ObjectID(
                    class_id="SkillInspectPanel", object_id="skill_panel"
                ),
                starting_height=50,
            ),
            registered_name=skill_panel_id,
            grouping_name="inspect_entity",
            camera=self.camera,
        )
        elements.append(skill_panel)

        self.setup_elements(elements)

        _ = (
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(8, 8, 284, 28),
                text=f"{skill_name}",
                manager=self.gui_manager,
                container=skill_panel.get_interactable(pygame_gui.elements.UIPanel),
                object_id=pygame_gui.core.ObjectID(
                    class_id="SkillLabel", object_id="skill_name"
                ),
            ),
        )

        _ = (
            pygame_gui.elements.UITextBox(
                relative_rect=pygame.Rect(8, 44, 284, 120),
                html_text=f"{skill_desc}",
                manager=self.gui_manager,
                container=skill_panel.get_interactable(pygame_gui.elements.UIPanel),
                object_id=pygame_gui.core.ObjectID(
                    class_id="SkillLabel", object_id="skill_desc"
                ),
            ),
        )

        self.temp_skill_panel_id = skill_panel_id

    @callback_event_bind("can_show_skill_panel")
    def skill_panel(self, msg: PageCallbackEvent) -> None:
        entity = self.entity
        panel_width = 160
        panel_x = 350
        panel_y = 100
        panel_id = "skill_panel"
        self.ability_panel_id = panel_id
        panel_rect = pygame.Rect(
            panel_x, panel_y, panel_width, len(entity.skills) * 30 + 30 + 10
        )
        panel_object = pygame_gui.elements.UIPanel(
            relative_rect=panel_rect,
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="SkillPanel", object_id=panel_id
            ),
        )

        panel_element = ui_element_wrapper(panel_object, panel_id, self.camera)
        self.setup_elements([panel_element])

        skill_buttons: list[ElementWrapper] = []

        # --- Create ability buttons inside the panel ---
        for i, skill in enumerate(entity.skills):
            element_id = f"skill_{i}"

            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(0, i * 30, 150, 30),
                text=f"{skill.name} ({skill.crumb_cost})",
                manager=self.gui_manager,
                container=panel_object,
                object_id=pygame_gui.core.ObjectID(
                    class_id="SkillButton", object_id=element_id
                ),
            )

            skill_buttons.append(
                ui_element_wrapper(
                    button,
                    element_id,
                    self.camera,
                    "SKILL_BUTTONS",
                    payload=IntegerPayload(skill.crumb_cost),
                )
            )

        # After all skills, add the "Move" button
        if isinstance(entity, Rodent):
            move_button_y = len(entity.skills) * 30  # Position after the last skill
            move_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(0, move_button_y, 150, 30),
                text=f"Move ({entity.move_cost})",
                manager=self.gui_manager,
                container=panel_object,
                object_id=pygame_gui.core.ObjectID(
                    class_id="SkillButton", object_id="skill_-1"
                ),
            )

            skill_buttons.append(
                ui_element_wrapper(
                    move_button,
                    "skill_-1",
                    self.camera,
                    "SKILL_BUTTONS",
                    payload=IntegerPayload(entity.move_cost),
                )
            )

        self.setup_elements(skill_buttons)
