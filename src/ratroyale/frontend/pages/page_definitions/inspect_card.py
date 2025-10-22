from ratroyale.coordination_manager import CoordinationManager

from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *


from ..page_managers.base_page import Page

from ratroyale.frontend.pages.page_managers.page_registry import register_page

from ratroyale.frontend.pages.page_elements.element import (
    ElementWrapper,
    ui_element_wrapper,
)
from ..page_elements.spatial_component import Camera

import pygame_gui
import pygame


@register_page
class InspectCard(Page):
    def __init__(
        self, coordination_manager: CoordinationManager, camera: Camera
    ) -> None:
        super().__init__(coordination_manager, camera)

    def define_initial_gui(self) -> list[ElementWrapper]:
        gui_elements: list[ElementWrapper] = []
        # === MainPanel ===
        panel_element = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(100, 80, 620, 460),
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="MainPanel", object_id="main_panel"
            ),
        )
        panel_element_wrapper = ui_element_wrapper(
            panel_element, "main_panel", self.camera
        )
        gui_elements.append(panel_element_wrapper)

        # === Rat image ===
        portrait_surface = pygame.Surface((140, 180), flags=pygame.SRCALPHA)
        portrait_surface.fill((200, 210, 255))  # placeholder
        pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect(20, 20, 80, 100),
            image_surface=portrait_surface,
            manager=self.gui_manager,
            container=panel_element,
        )

        # === Name ===
        pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(110, 20, 200, 28),
            html_text="NAME :",
            manager=self.gui_manager,
            container=panel_element,
            object_id=pygame_gui.core.ObjectID(
                class_id="NameTitle", object_id="char_name"
            ),
        )

        # === Description ===
        pygame_gui.elements.UITextBox(
            html_text="DESCRIPTION",
            relative_rect=pygame.Rect(110, 45, 480, 90),
            manager=self.gui_manager,
            container=panel_element,
            object_id=pygame_gui.core.ObjectID(class_id="Desc", object_id="desc"),
        )

        # === Stat_panel ===
        stats_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(20, 140, 200, 295),
            manager=self.gui_manager,
            container=panel_element,
            object_id=pygame_gui.core.ObjectID(
                class_id="StatsPanel", object_id="stats_panel"
            ),
        )
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(80, 5, 40, 20),
            text="STATS",
            manager=self.gui_manager,
            container=stats_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="StatsHeader", object_id="stats_header"
            ),
        )

        # === StatsRows ===
        stat_data = {
            "HP": "7",
            "SPEED": "3",
            "DEFENSE": "3",
            "ATTACK": "10",
            "STAMINA": "2",
            "MOVE COST": "3",
            "CRUMB COST": "25",
            "HEIGHT": "0",
        }

        y = 36
        for key, value in stat_data.items():
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(0, y, 120, 22),
                text=f"{key}:",
                manager=self.gui_manager,
                container=stats_panel,
                object_id=pygame_gui.core.ObjectID(
                    class_id="StatKey", object_id=f"key_{key}"
                ),
            )
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(100, y, 100, 22),
                text=value,
                manager=self.gui_manager,
                container=stats_panel,
                object_id=pygame_gui.core.ObjectID(
                    class_id="StatVal", object_id=f"val_{key}"
                ),
            )
            y += 30

        # === Skills Panel ===
        skills_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(220, 140, 370, 295),
            manager=self.gui_manager,
            container=panel_element,
        )

        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 6, 130, 22),
            text="SKILLS & PASSIVES",
            manager=self.gui_manager,
            container=skills_panel,
            anchors={"centerx": "centerx", "top": "top"},
        )

        # === Scroll Container ===
        scroll_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(7, 30, 350, 255),
            manager=self.gui_manager,
            container=skills_panel,
            allow_scroll_x=False,  # disable horizontal scroll
        )

        y_offset = 0
        # --- Active Skills Header ---
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(5, y_offset, 200, 25),
            text="------- Active Skills -------",
            manager=self.gui_manager,
            container=scroll_container,
        )
        y_offset += 30

        active_skills = [
            (
                "Railgun Charge",
                "If it doesn't have <u>Railgun Cooldown</u> status effect, charge its weapon and give itself Railgun Charged status effect at the end of the turn. The effect lasts for 2 turn. "
                "<br><b>Crumb Cost: 20</b>",
            ),
            (
                "Railgun",
                "If it has <u>Railgun Charged</u> status effect, shoot the weapon at an enemy dealing ATK*2 damage and clear said effect and give new <u>Railgun Cooldown</u> status effect that last for 1 turn. "
                "<br><b>Reach: 20, Altitude: 0, Crumb Cost: 5</b>",
            ),
        ]
        for skill_name, desc in active_skills:
            y_offset += self._create_skill_card(
                scroll_container, skill_name, desc, y_offset
            )

        # --- Passive Skills Header ---
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(5, y_offset, 200, 25),
            text="-------- Passive Skills -------",
            manager=self.gui_manager,
            container=scroll_container,
        )
        y_offset += 30

        passive_skills = [
            (
                "High ground",
                "When being at higher tile than the target, reach of all skills +1",
            ),
            ("Top OP", "Cannot attack base"),
        ]
        for skill_name, desc in passive_skills:
            y_offset += self._create_skill_card(
                scroll_container, skill_name, desc, y_offset
            )

        # expand scrollable area to fit all skills
        scroll_container.set_scrollable_area_dimensions((350, y_offset + 20))

        return gui_elements

    def _create_skill_card(
        self,
        parent_container: pygame_gui.elements.UIScrollingContainer,
        name: str,
        description: str,
        y_start: int,
    ) -> int:

        card_width = 330
        padding = 10
        image_size = 50

        # === Base card ===
        skill_card = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, y_start, card_width, 60),
            manager=self.gui_manager,
            container=parent_container,
        )

        # === Skill image ===
        portrait_surface = pygame.Surface(
            (image_size, image_size), flags=pygame.SRCALPHA
        )
        portrait_surface.fill((220, 220, 255))
        pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect(0, 0, image_size, image_size),
            image_surface=portrait_surface,
            manager=self.gui_manager,
            container=skill_card,
        )

        # === Name ===
        pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(60, 0, 150, 35),
            html_text=f"{name}",
            manager=self.gui_manager,
            container=skill_card,
        )

        # === Description  ===
        desc_box = pygame_gui.elements.UITextBox(
            html_text=f"Description: <font size=3>{description}</font>",
            relative_rect=pygame.Rect(60, 30, 260, 10),
            manager=self.gui_manager,
            container=skill_card,
            wrap_to_height=True,
        )

        # === dynamically expand height ===
        text_height = int(desc_box.get_relative_rect().height)
        desc_box.set_dimensions((260, text_height))
        total_height = max(image_size, 40 + text_height)

        skill_card.set_dimensions((card_width, total_height))
        return total_height + padding
