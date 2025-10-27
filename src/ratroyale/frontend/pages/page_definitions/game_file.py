import pygame
import pygame_gui

from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.visual_token import *
from ratroyale.frontend.pages.page_managers.event_binder import input_event_bind
from ratroyale.frontend.pages.page_managers.page_registry import register_page

from ratroyale.frontend.pages.page_elements.element import (
    ElementWrapper,
    ui_element_wrapper,
)
from ratroyale.frontend.pages.page_elements.spatial_component import (
    Camera,
)
from ratroyale.frontend.visual.screen_constants import SCREEN_SIZE, SCREEN_SIZE_HALVED


from ..page_managers.base_page import Page


@register_page
class GameFilePage(Page):
    def __init__(
        self, coordination_manager: CoordinationManager, camera: Camera
    ) -> None:
        super().__init__(
            coordination_manager, theme_name="select_player", camera=camera
        )

    def define_initial_gui(self) -> list[ElementWrapper]:
        """Return all GUI elements for the select player page."""
        print("HEllo")
        elements: list[ElementWrapper] = []

        screen_width, screen_height = SCREEN_SIZE

        # Top title
        # Title
        title_element = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(SCREEN_SIZE_HALVED[0], 20, 400, 60),
            text="Select Player",
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="SelectPlayerTitle", object_id="title"
            ),
        )
        elements.append(
            ui_element_wrapper(title_element, "select_player_title", self.camera)
        )

        # Panels
        panel_width = 500
        panel_height = 150
        panel_padding = 20
        total_height = 3 * panel_height + 2 * panel_padding
        start_y = (screen_height - total_height) // 2

        panel_texts = [
            "ExamplePlayer\nLevel: 5\nHP: 100\nAttack: 20",  # top panel with example player
            "-- No player data --",
            "-- No player data --",
        ]

        for i, text in enumerate(panel_texts):
            panel_rect = pygame.Rect(
                (screen_width - panel_width) // 2,
                start_y + i * (panel_height + panel_padding),
                panel_width,
                panel_height,
            )

            # Create the panel (background with border)
            panel_element = pygame_gui.elements.UIPanel(
                relative_rect=panel_rect,
                manager=self.gui_manager,
                object_id=pygame_gui.core.ObjectID(
                    class_id="SelectPlayerPanel", object_id=f"panel_{i}"
                ),
            )
            elements.append(
                ui_element_wrapper(panel_element, f"panel_{i}", self.camera)
            )

            # Create the label inside the panel
            label_rect = pygame.Rect(10, 10, panel_width - 20, panel_height - 20)
            _ = pygame_gui.elements.UILabel(
                relative_rect=label_rect,
                text=text,
                manager=self.gui_manager,
                object_id=pygame_gui.core.ObjectID(
                    class_id="SelectPlayerPanelLabel", object_id=f"panel_label_{i}"
                ),
                container=panel_element,
            )

        # Bottom buttons side by side
        button_width = 200
        button_height = 50
        button_padding = 40
        bottom_y = start_y + total_height
        buttons = [("CREATE_NEW", "CREATE NEW"), ("DELETE", "DELETE")]

        total_button_width = 2 * button_width + button_padding
        start_x = (screen_width - total_button_width) // 2

        for i, (btn_id, text) in enumerate(buttons):
            btn_rect = pygame.Rect(
                start_x + i * (button_width + button_padding),
                bottom_y,
                button_width,
                button_height,
            )
            print(btn_rect)
            button = pygame_gui.elements.UIButton(
                relative_rect=btn_rect,
                text=text,
                manager=self.gui_manager,
                object_id=pygame_gui.core.ObjectID(
                    class_id="SelectPlayerButton", object_id=btn_id
                ),
            )
            elements.append(ui_element_wrapper(button, btn_id, self.camera))

        return elements

    # region Input Responses
    @input_event_bind("CREATE_NEW", pygame_gui.UI_BUTTON_PRESSED)
    def _on_create_new_click(self, msg: pygame.event.Event) -> None:
        # Example: open create new player page
        self.post(
            PageNavigationEvent(action_list=[(PageNavigation.OPEN, "CreatePlayerPage")])
        )

    @input_event_bind("DELETE", pygame_gui.UI_BUTTON_PRESSED)
    def _on_delete_click(self, msg: pygame.event.Event) -> None:
        # Example: delete selected player
        print("Delete button pressed. Implement deletion logic here.")
