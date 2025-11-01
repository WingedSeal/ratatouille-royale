import pygame
import pygame_gui

from ratroyale.backend.player_info.squeak import Squeak
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
        super().__init__(coordination_manager, camera)
        self.current_squeak: Squeak | None = None
        self.main_panel: pygame_gui.elements.UIPanel | None = None

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

        rodent_cls = squeak.rodent

        panel_w, panel_h = 620, 460
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
        desc_text = "No description available"
        if rodent_cls:
            desc_text = getattr(rodent_cls, "description", "No description available")
        pygame_gui.elements.UITextBox(
            html_text=desc_text,
            relative_rect=pygame.Rect(110, 45, 480, 90),
            manager=self.gui_manager,
            container=self.main_panel,
            object_id=pygame_gui.core.ObjectID(class_id="Desc", object_id="desc"),
            anchors={"left": "left", "top": "top"},
        )
        stats_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(20, 140, 200, 295),
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
            "HP": str(getattr(rodent_cls, "health", "N/A") if rodent_cls else "N/A"),
            "SPEED": str(getattr(rodent_cls, "speed", "N/A") if rodent_cls else "N/A"),
            "DEFENSE": str(
                getattr(rodent_cls, "defense", "N/A") if rodent_cls else "N/A"
            ),
            "ATTACK": str(
                getattr(rodent_cls, "attack", "N/A") if rodent_cls else "N/A"
            ),
            "STAMINA": str(
                getattr(rodent_cls, "max_move_stamina", "N/A") if rodent_cls else "N/A"
            ),
            "MOVE COST": str(
                getattr(rodent_cls, "move_cost", "N/A") if rodent_cls else "N/A"
            ),
            "CRUMB COST": str(squeak.crumb_cost),
            "HEIGHT": str(
                getattr(rodent_cls, "height", "N/A") if rodent_cls else "N/A"
            ),
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
            relative_rect=pygame.Rect(220, 140, 370, 295),
            manager=self.gui_manager,
            container=self.main_panel,
            anchors={"left": "left", "top": "top"},
        )

        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 6, 130, 22),
            text="SKILLS & PASSIVES",
            manager=self.gui_manager,
            container=skills_panel,
            anchors={"centerx": "centerx", "top": "top"},
        )
        scroll_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(7, 30, 350, 255),
            manager=self.gui_manager,
            container=skills_panel,
            allow_scroll_x=False,
            anchors={"left": "left", "top": "top"},
        )

        y_offset = 0
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(5, y_offset, 200, 25),
            text="------- Active Skills -------",
            manager=self.gui_manager,
            container=scroll_container,
            anchors={"left": "left", "top": "top"},
        )
        y_offset += 30

        # Get real skills from rodent class
        if rodent_cls:
            # Get skill descriptions from rodent
            try:
                # Create a temporary instance to call skill_descriptions
                temp_rodent = rodent_cls(pos=None, side=None)  # type: ignore[arg-type]
                skill_descriptions = temp_rodent.skill_descriptions()
                for skill_desc in skill_descriptions:
                    # skill_desc is typically a string, extract name and description
                    # Format might vary, so we'll handle it gracefully
                    y_offset += self._create_skill_card(
                        scroll_container, "Skill", skill_desc, y_offset
                    )
            except Exception:
                pass  # If we can't get skills, just skip

        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(5, y_offset, 200, 25),
            text="-------- Passive Skills -------",
            manager=self.gui_manager,
            container=scroll_container,
            anchors={"left": "left", "top": "top"},
        )
        y_offset += 30

        # Get passive skills from rodent class
        if rodent_cls:
            try:
                temp_rodent = rodent_cls(pos=None, side=None)  # type: ignore[arg-type]
                passive_descriptions = temp_rodent.passive_descriptions()
                for skill_name, skill_desc in passive_descriptions:
                    y_offset += self._create_skill_card(
                        scroll_container, skill_name, skill_desc, y_offset
                    )
            except Exception:
                pass  # If we can't get passives, just skip

        scroll_container.set_scrollable_area_dimensions((350, y_offset + 20))

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
            anchors={"left": "left", "top": "top"},
        )
        desc_box = pygame_gui.elements.UITextBox(
            html_text=f"Description: <font size=3>{description}</font>",
            relative_rect=pygame.Rect(60, 30, 260, 10),
            manager=self.gui_manager,
            container=skill_card,
            wrap_to_height=True,
            anchors={"left": "left", "top": "top"},
        )
        text_height = int(desc_box.get_relative_rect().height)
        desc_box.set_dimensions((260, text_height))
        total_height = max(image_size, 40 + text_height)

        skill_card.set_dimensions((card_width, total_height))
        return total_height + padding

    @input_event_bind("close_button", pygame_gui.UI_BUTTON_PRESSED)
    def close_panel(self, msg: pygame.event.Event) -> None:
        self.post(
            PageNavigationEvent(action_list=[(PageNavigation.CLOSE, "InspectSqueak")])
        )
