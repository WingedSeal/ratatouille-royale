import pygame
import pygame_gui

from ratroyale.backend.ai.rushb_ai import RushBAI
from ratroyale.backend.player_info.preset_player_info import (
    AI_PLAYER_INFO,
    get_default_player_info,
)
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.payloads import BackendStartPayload
from ratroyale.event_tokens.visual_token import *
from ratroyale.frontend.pages.page_managers.event_binder import input_event_bind
from ratroyale.frontend.pages.page_managers.page_registry import register_page

from ratroyale.backend.side import Side
from ratroyale.frontend.pages.page_elements.element import (
    ElementWrapper,
    ui_element_wrapper,
)
from ratroyale.frontend.pages.page_elements.spatial_component import (
    Camera,
)
from pathlib import Path


from ..page_managers.base_page import Page
from ratroyale.backend.map import Map
from ratroyale.backend.ai.base_ai import BaseAI
from ratroyale.backend.ai.random_ai import RandomAI


# TODO: make helpers to make button registration easier
@register_page
class ChoosePlayer(Page):
    def __init__(
        self, coordination_manager: CoordinationManager, camera: Camera
    ) -> None:
        super().__init__(coordination_manager, theme_name="main_menu", camera=camera)
        self.map = Map.from_file(
            Path(__file__).parents[3] / "map_file/starting-kitchen.rrmap"
        )
        self.ai_type: type[BaseAI] | None = None

    def define_initial_gui(self) -> list[ElementWrapper]:
        """Return all GUI elements for the main menu page, auto-stacked vertically."""
        elements: list[ElementWrapper] = []

        button_specs = [
            ("vs_human", "vs. HUMAN"),
            ("vs_rush_b_ai", "vs. RUSHB AI"),
            ("vs_random_ai", "vs. RANDOM AI"),
        ]

        start_x = 100
        start_y = 100
        button_width = 200
        button_height = 50
        padding = 10  # space between buttons

        for i, (button_id, text) in enumerate(button_specs):
            button_rect = pygame.Rect(
                start_x,
                start_y + i * (button_height + padding),
                button_width,
                button_height,
            )
            button = pygame_gui.elements.UIButton(
                relative_rect=button_rect,
                text=text,
                manager=self.gui_manager,
                object_id=pygame_gui.core.ObjectID(
                    class_id="MainMenuButton", object_id=button_id
                ),
            )
            elements.append(ui_element_wrapper(button, button_id, self.camera))

        return elements

    # region Input Responses

    @input_event_bind("vs_human", pygame_gui.UI_BUTTON_PRESSED)
    def vs_human(self, msg: pygame.event.Event) -> None:
        self.start_game()

    @input_event_bind("vs_random_ai", pygame_gui.UI_BUTTON_PRESSED)
    def vs_random_ai(self, msg: pygame.event.Event) -> None:
        self.ai_type = RandomAI
        self.start_game()

    @input_event_bind("vs_rush_b_ai", pygame_gui.UI_BUTTON_PRESSED)
    def vs_rushb_ai(self, msg: pygame.event.Event) -> None:
        self.ai_type = RushBAI
        self.start_game()

    def start_game(self) -> None:
        assert self.map
        self.post(
            GameManagerEvent(
                "start",
                BackendStartPayload(
                    self.map,
                    get_default_player_info(),
                    AI_PLAYER_INFO["Balanced"],
                    Side.RAT,
                    self.ai_type,
                ),
            )
        )
        self.close_self()
        self.open_page("GameBoard")
        self.open_page("GameInfoPage")
        self.open_page("PauseButton")

    # endregion
