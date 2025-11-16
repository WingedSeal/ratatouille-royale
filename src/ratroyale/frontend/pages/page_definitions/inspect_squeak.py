import pygame
import pygame_gui

from ratroyale.backend.player_info.squeak import (
    Squeak,
    RodentSqueakInfo,
    TrickSqueakInfo,
)
from ratroyale.backend.hexagon import OddRCoord
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.input_token import get_payload_from_msg
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.payloads import SqueakPayload
from ratroyale.event_tokens.visual_token import *
from ratroyale.frontend.pages.page_elements.element import ElementWrapper
from ratroyale.frontend.pages.page_managers.event_binder import (
    callback_event_bind,
    input_event_bind,
    SpecialInputScope,
)
from ratroyale.frontend.pages.page_managers.page_registry import register_page

from ..page_elements.spatial_component import Camera
from ..page_managers.base_page import Page
from ratroyale.frontend.visual.screen_constants import SCREEN_SIZE


@register_page
class InspectSqueak(Page):
    def __init__(
        self, coordination_manager: CoordinationManager, camera: Camera
    ) -> None:
        super().__init__(
            coordination_manager,
            camera=camera,
            theme_name="inspect_squeak",
            is_blocking=True,
            base_color=(0, 0, 0, 128),
        )
        self.current_squeak: Squeak | None = None
        self.main_panel: pygame_gui.elements.UIPanel | None = None
        self.scroll_container: pygame_gui.elements.UIScrollingContainer | None = None

    def define_initial_gui(self) -> list[ElementWrapper]:
        return []

    @callback_event_bind("squeak_data")
    def show_squeak_data(self, msg: PageCallbackEvent) -> None:
        """Populate UI with real squeak data from GameBoard."""
        if msg.success and msg.payload:
            payload = get_payload_from_msg(msg, SqueakPayload)
            if not payload:
                return

            squeak = payload.squeak
            self.current_squeak = squeak
            self._create_squeak_ui(squeak)

    def _create_squeak_ui(self, squeak: Squeak) -> None:
        """Create fresh UI elements with squeak data."""
        if self.main_panel:
            self.main_panel.kill()  # type: ignore[no-untyped-call]

        # Handle RODENT type squeaks
        if isinstance(squeak.squeak_info, RodentSqueakInfo):
            self._create_rodent_squeak_ui(squeak, squeak.squeak_info)
        # Handle TRICK type squeaks
        elif isinstance(squeak.squeak_info, TrickSqueakInfo):
            self._create_trick_squeak_ui(squeak, squeak.squeak_info)

    def _create_rodent_squeak_ui(
        self, squeak: Squeak, squeak_info: RodentSqueakInfo
    ) -> None:
        """Create UI for RODENT type squeaks."""
        rodent_cls = squeak_info.rodent

        panel_w, panel_h = 700, 520
        panel_x = (SCREEN_SIZE[0] - panel_w) // 2
        panel_y = (SCREEN_SIZE[1] - panel_h) // 2
        self.main_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(panel_x, panel_y, panel_w, panel_h),
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="MainPanel", object_id="main_panel"
            ),
            anchors={"left": "left", "top": "top"},
        )
        pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(-40, 12, 28, 28),
            text="x",
            manager=self.gui_manager,
            container=self.main_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="CloseButton", object_id="close_button"
            ),
            anchors={"right": "right", "top": "top"},
        )
        portrait_surface = pygame.Surface((140, 180), flags=pygame.SRCALPHA)
        portrait_surface.fill((200, 210, 255))
        pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect(20, 20, 80, 100),
            image_surface=portrait_surface,
            manager=self.gui_manager,
            container=self.main_panel,
            anchors={"left": "left", "top": "top"},
        )
        name_text = f"<b>{squeak.name}</b>"
        pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(110, 20, 200, 28),
            html_text=name_text,
            manager=self.gui_manager,
            container=self.main_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="NameTitle", object_id="char_name"
            ),
            anchors={"left": "left", "top": "top"},
        )
        desc_text = rodent_cls.description
        pygame_gui.elements.UITextBox(
            html_text=desc_text,
            relative_rect=pygame.Rect(110, 45, 480, 90),
            manager=self.gui_manager,
            container=self.main_panel,
            object_id=pygame_gui.core.ObjectID(class_id="Desc", object_id="desc"),
            anchors={"left": "left", "top": "top"},
        )
        stats_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(20, 140, 220, 355),
            manager=self.gui_manager,
            container=self.main_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="StatsPanel", object_id="stats_panel"
            ),
            anchors={"left": "left", "top": "top"},
        )
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(80, 5, 40, 20),
            text="STATS",
            manager=self.gui_manager,
            container=stats_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="StatsHeader", object_id="stats_header"
            ),
            anchors={"left": "left", "top": "top"},
        )

        # === StatsRows with real data from rodent class ===
        stat_data = {
            "HP": str(rodent_cls.health),
            "Speed": str(rodent_cls.speed),
            "Defense": str(rodent_cls.defense),
            "Attack": str(rodent_cls.attack),
            "Move Stamina": str(rodent_cls.max_move_stamina),
            "Move Cost": str(rodent_cls.move_cost),
            "Crumb Cost": str(squeak.crumb_cost),
            "Skill Stamina": str(rodent_cls.skill_stamina),
            "Height": str(rodent_cls.height),
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
                anchors={"left": "left", "top": "top"},
            )
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(100, y, 100, 22),
                text=value,
                manager=self.gui_manager,
                container=stats_panel,
                object_id=pygame_gui.core.ObjectID(
                    class_id="StatVal", object_id=f"val_{key}"
                ),
                anchors={"left": "left", "top": "top"},
            )
            y += 30
        skills_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(250, 140, 430, 355),
            manager=self.gui_manager,
            container=self.main_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="SkillsPanel", object_id="skills_panel"
            ),
            anchors={"left": "left", "top": "top"},
        )

        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 6, 130, 22),
            text="SKILLS & PASSIVES",
            manager=self.gui_manager,
            container=skills_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="SkillsPanelHeader", object_id="skills_panel_header"
            ),
            anchors={"centerx": "centerx", "top": "top"},
        )
        scroll_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(7, 30, 410, 315),
            manager=self.gui_manager,
            container=skills_panel,
            allow_scroll_x=False,
            anchors={"left": "left", "top": "top"},
        )
        self.scroll_container = scroll_container

        y_offset = 0
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(5, y_offset, 200, 25),
            text="------- Active Skills -------",
            manager=self.gui_manager,
            container=scroll_container,
            object_id=pygame_gui.core.ObjectID(
                class_id="SkillsHeader", object_id="active_skills_header"
            ),
            anchors={"left": "left", "top": "top"},
        )
        y_offset += 30

        temp_rodent = rodent_cls(pos=OddRCoord(0, 0), side=None)
        for i, skill_desc in enumerate(temp_rodent.skill_descriptions()):
            skill_name = (
                temp_rodent.skills[i].name
                if i < len(temp_rodent.skills)
                else f"Skill {i}"
            )
            # Add skill stats if available
            skill_obj = temp_rodent.skills[i] if i < len(temp_rodent.skills) else None
            if skill_obj:
                reach = skill_obj.reach if hasattr(skill_obj, "reach") else None
                altitude = (
                    skill_obj.altitude if hasattr(skill_obj, "altitude") else None
                )
                crumb_cost = (
                    skill_obj.crumb_cost if hasattr(skill_obj, "crumb_cost") else None
                )

                stats_info = []
                if reach is not None:
                    stats_info.append(f"Reach: {reach}")
                if altitude is not None:
                    stats_info.append(f"Altitude: {altitude}")
                if crumb_cost is not None:
                    stats_info.append(f"Cost: {crumb_cost}")

                if stats_info:
                    skill_desc = f"{skill_desc}<br>({', '.join(stats_info)})"

            y_offset += self._create_skill_card(
                scroll_container, skill_name, skill_desc, y_offset
            )

        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(5, y_offset, 200, 25),
            text="-------- Passive Skills -------",
            manager=self.gui_manager,
            container=scroll_container,
            object_id=pygame_gui.core.ObjectID(
                class_id="SkillsHeader", object_id="passive_skills_header"
            ),
            anchors={"left": "left", "top": "top"},
        )
        y_offset += 30

        for skill_name, skill_desc in temp_rodent.passive_descriptions():
            y_offset += self._create_skill_card(
                scroll_container, skill_name, skill_desc, y_offset
            )

        scroll_container.set_scrollable_area_dimensions((410, y_offset + 20))

    def _create_trick_squeak_ui(
        self, squeak: Squeak, squeak_info: TrickSqueakInfo
    ) -> None:
        """Create UI for TRICK type squeaks with related entities."""
        panel_w, panel_h = 700, 520
        panel_x = (SCREEN_SIZE[0] - panel_w) // 2
        panel_y = (SCREEN_SIZE[1] - panel_h) // 2
        self.main_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(panel_x, panel_y, panel_w, panel_h),
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="MainPanel", object_id="main_panel"
            ),
            anchors={"left": "left", "top": "top"},
        )
        pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(-40, 12, 28, 28),
            text="x",
            manager=self.gui_manager,
            container=self.main_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="CloseButton", object_id="close_button"
            ),
            anchors={"right": "right", "top": "top"},
        )

        # Portrait placeholder
        portrait_surface = pygame.Surface((140, 180), flags=pygame.SRCALPHA)
        portrait_surface.fill((200, 210, 255))
        pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect(20, 20, 80, 100),
            image_surface=portrait_surface,
            manager=self.gui_manager,
            container=self.main_panel,
            anchors={"left": "left", "top": "top"},
        )

        # Name title
        name_text = f"<b>{squeak.name}</b>"
        pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(110, 20, 200, 28),
            html_text=name_text,
            manager=self.gui_manager,
            container=self.main_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="NameTitle", object_id="char_name"
            ),
            anchors={"left": "left", "top": "top"},
        )

        # Description
        desc_text = squeak_info.description
        pygame_gui.elements.UITextBox(
            html_text=desc_text,
            relative_rect=pygame.Rect(110, 45, 480, 90),
            manager=self.gui_manager,
            container=self.main_panel,
            object_id=pygame_gui.core.ObjectID(class_id="Desc", object_id="desc"),
            anchors={"left": "left", "top": "top"},
        )

        # Stats panel - display trick-specific stats
        stats_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(20, 140, 220, 355),
            manager=self.gui_manager,
            container=self.main_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="StatsPanel", object_id="stats_panel"
            ),
            anchors={"left": "left", "top": "top"},
        )
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(80, 5, 40, 20),
            text="STATS",
            manager=self.gui_manager,
            container=stats_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="StatsHeader", object_id="stats_header"
            ),
            anchors={"left": "left", "top": "top"},
        )

        # Trick-specific stats
        # Get stats from the first entity class in related_entities
        trick_cls = (
            squeak_info.related_entities[0] if squeak_info.related_entities else None
        )

        stat_data = {
            "Crumb Cost": str(squeak.crumb_cost),
        }

        # Add entity properties if available
        if trick_cls:
            stat_data["Health"] = str(trick_cls.health)
            stat_data["Defense"] = str(trick_cls.defense)
            stat_data["Height"] = str(trick_cls.height)

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
                anchors={"left": "left", "top": "top"},
            )
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(100, y, 100, 22),
                text=value,
                manager=self.gui_manager,
                container=stats_panel,
                object_id=pygame_gui.core.ObjectID(
                    class_id="StatVal", object_id=f"val_{key}"
                ),
                anchors={"left": "left", "top": "top"},
            )
            y += 30

        # Skills & Passives panel (render like rodents)
        skills_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(250, 140, 430, 355),
            manager=self.gui_manager,
            container=self.main_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="SkillsPanel", object_id="skills_panel"
            ),
            anchors={"left": "left", "top": "top"},
        )

        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 6, 130, 22),
            text="SKILLS & PASSIVES",
            manager=self.gui_manager,
            container=skills_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="SkillsPanelHeader", object_id="skills_panel_header"
            ),
            anchors={"centerx": "centerx", "top": "top"},
        )

        scroll_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(7, 30, 410, 315),
            manager=self.gui_manager,
            container=skills_panel,
            allow_scroll_x=False,
            anchors={"left": "left", "top": "top"},
        )
        self.scroll_container = scroll_container

        y_offset = 0

        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(5, y_offset, 200, 25),
            text="------- Active Skills -------",
            manager=self.gui_manager,
            container=scroll_container,
            object_id=pygame_gui.core.ObjectID(
                class_id="SkillsHeader", object_id="active_skills_header"
            ),
            anchors={"left": "left", "top": "top"},
        )
        y_offset += 30

        if trick_cls:
            temp_trick = trick_cls(pos=OddRCoord(0, 0), side=None)

            # If the trick provides active skill descriptions, render them; otherwise show none
            if hasattr(temp_trick, "skill_descriptions"):
                for i, skill_desc in enumerate(temp_trick.skill_descriptions()):
                    skill_name = (
                        temp_trick.skills[i].name
                        if i < len(temp_trick.skills)
                        else f"Skill {i}"
                    )
                    # Add skill stats if available on the skill object
                    skill_obj = (
                        temp_trick.skills[i] if i < len(temp_trick.skills) else None
                    )
                    if skill_obj:
                        stats_info = []
                        # skill objects may have reach/altitude/crumb_cost like rodents
                        if getattr(skill_obj, "reach", None) is not None:
                            stats_info.append(f"Reach: {skill_obj.reach}")
                        if getattr(skill_obj, "altitude", None) is not None:
                            stats_info.append(f"Altitude: {skill_obj.altitude}")
                        if getattr(skill_obj, "crumb_cost", None) is not None:
                            stats_info.append(f"Cost: {skill_obj.crumb_cost}")
                        if stats_info:
                            skill_desc = f"{skill_desc}<br>({', '.join(stats_info)})"

                    y_offset += self._create_skill_card(
                        scroll_container, skill_name, skill_desc, y_offset
                    )
            else:
                # No active skills - show a simple label
                pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect(5, y_offset, 300, 22),
                    text="(No active skills)",
                    manager=self.gui_manager,
                    container=scroll_container,
                    anchors={"left": "left", "top": "top"},
                )
                y_offset += 30

            # Passive skills header
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(5, y_offset, 200, 25),
                text="-------- Passive Skills -------",
                manager=self.gui_manager,
                container=scroll_container,
                object_id=pygame_gui.core.ObjectID(
                    class_id="SkillsHeader", object_id="passive_skills_header"
                ),
                anchors={"left": "left", "top": "top"},
            )
            y_offset += 30

            for skill_name, skill_desc in temp_trick.passive_descriptions():
                y_offset += self._create_skill_card(
                    scroll_container, skill_name, skill_desc, y_offset
                )

        scroll_container.set_scrollable_area_dimensions((410, y_offset + 20))

    def _create_entity_card(
        self,
        parent_container: pygame_gui.elements.UIScrollingContainer,
        entity_cls: type,
        y_start: int,
    ) -> int:
        """Create a card for displaying entity information."""
        card_width = 550
        padding = 10
        image_size = 50

        entity_card = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, y_start, card_width, 70),
            manager=self.gui_manager,
            container=parent_container,
            object_id=pygame_gui.core.ObjectID(
                class_id="EntityCard", object_id="entity_card"
            ),
            anchors={"left": "left", "top": "top"},
        )
        portrait_surface = pygame.Surface(
            (image_size, image_size), flags=pygame.SRCALPHA
        )
        portrait_surface.fill((200, 200, 200))
        pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect(0, 0, image_size, image_size),
            image_surface=portrait_surface,
            manager=self.gui_manager,
            container=entity_card,
            anchors={"left": "left", "top": "top"},
        )

        entity_name = getattr(entity_cls, "name", entity_cls.__name__)
        pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(60, 10, 480, 50),
            html_text=f"<b>{entity_name}</b>",
            manager=self.gui_manager,
            container=entity_card,
            object_id=pygame_gui.core.ObjectID(
                class_id="EntityName", object_id="entity_name"
            ),
            anchors={"left": "left", "top": "top"},
        )

        entity_card.set_dimensions((card_width, image_size + padding))
        return image_size + padding

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

        skill_card = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, y_start, card_width, 60),
            manager=self.gui_manager,
            container=parent_container,
            object_id=pygame_gui.core.ObjectID(
                class_id="SkillCard", object_id="skill_card"
            ),
            anchors={"left": "left", "top": "top"},
        )
        portrait_surface = pygame.Surface(
            (image_size, image_size), flags=pygame.SRCALPHA
        )
        portrait_surface.fill((220, 220, 255))
        pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect(0, 0, image_size, image_size),
            image_surface=portrait_surface,
            manager=self.gui_manager,
            container=skill_card,
            anchors={"left": "left", "top": "top"},
        )
        pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(60, 0, 150, 35),
            html_text=f"{name}",
            manager=self.gui_manager,
            container=skill_card,
            object_id=pygame_gui.core.ObjectID(
                class_id="SkillName", object_id="skill_name"
            ),
            anchors={"left": "left", "top": "top"},
        )
        desc_box = pygame_gui.elements.UITextBox(
            html_text=f"<font size=3>{description}</font>",
            relative_rect=pygame.Rect(60, 30, 260, 10),
            manager=self.gui_manager,
            container=skill_card,
            object_id=pygame_gui.core.ObjectID(
                class_id="SkillDesc", object_id="skill_desc"
            ),
            wrap_to_height=True,
            anchors={"left": "left", "top": "top"},
        )
        text_height = int(desc_box.get_relative_rect().height)
        desc_box.set_dimensions((260, text_height))
        total_height = max(image_size, 40 + text_height)

        skill_card.set_dimensions((card_width, total_height))
        return total_height + padding

    @input_event_bind(SpecialInputScope.GLOBAL, pygame.MOUSEWHEEL)
    def on_mousewheel(self, msg: pygame.event.Event) -> None:
        """Block mousewheel events when hovering over the scroll container."""
        if self.scroll_container:
            mouse_pos = pygame.mouse.get_pos()
            container_rect = self.scroll_container.rect
            assert container_rect is not None
            if container_rect.collidepoint(mouse_pos):
                return  # Consume event to prevent GameBoard scrolling

    @input_event_bind("close_button", pygame_gui.UI_BUTTON_PRESSED)
    def close_panel(self, msg: pygame.event.Event) -> None:
        self.post(
            PageNavigationEvent(action_list=[(PageNavigation.CLOSE, "InspectSqueak")])
        )
