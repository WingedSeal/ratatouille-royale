import pygame
import pygame_gui

from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.payloads import PlayerInfoPayload
from ratroyale.event_tokens.visual_token import *
from ratroyale.frontend.pages.page_managers.event_binder import (
    input_event_bind,
    callback_event_bind,
)
from ratroyale.frontend.pages.page_managers.page_registry import register_page

from ratroyale.frontend.pages.page_elements.element import (
    ElementWrapper,
    ui_element_wrapper,
)
from ratroyale.frontend.pages.page_elements.spatial_component import (
    Camera,
)

from ratroyale.game_data import RRMAPS_DIR_PATH


from ..page_managers.base_page import Page
from ratroyale.backend.map import Map
from ratroyale.backend.ai.base_ai import BaseAI


# TODO: make helpers to make button registration easier
@register_page
class ChoosePlayer(Page):
    def __init__(
        self, coordination_manager: CoordinationManager, camera: Camera
    ) -> None:
        super().__init__(coordination_manager, theme_name="main_menu", camera=camera)
        self.map = Map.from_file(RRMAPS_DIR_PATH / "starting-kitchen.rrmap")
        self.ai_type: type[BaseAI] | None = None

    def define_initial_gui(self) -> list[ElementWrapper]:
        """Return all GUI elements for the main menu page, auto-stacked vertically."""
        elements: list[ElementWrapper] = []

        button_specs = [
            ("local_multiplayer", "Local Multiplayer"),
            ("vs_rush_b_ai", "vs. RushB AI"),
            ("vs_random_ai", "vs. Random AI"),
            ("go_back", "GO BACK"),
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

    @input_event_bind("local_multiplayer", pygame_gui.UI_BUTTON_PRESSED)
    def local_multiplayer(self, msg: pygame.event.Event) -> None:
        self.post(PageCallbackEvent("local_multiplayer_clicked"))
        self.open_page("ChooseAIPlayerInfo")
        self.post(
            PageCallbackEvent(
                "send_player_info",
                payload=PlayerInfoPayload(self.player_1_info, self.player_1_path),
            )
        )
        self.close_self()

    @input_event_bind("vs_random_ai", pygame_gui.UI_BUTTON_PRESSED)
    def vs_random_ai(self, msg: pygame.event.Event) -> None:
        self.open_page("ChooseAIPlayerInfo")
        self.post(PageCallbackEvent("vs_random_ai_clicked"))
        self.post(
            PageCallbackEvent(
                "send_player_info",
                payload=PlayerInfoPayload(self.player_1_info, self.player_1_path),
            )
        )
        self.close_self()

    @input_event_bind("vs_rush_b_ai", pygame_gui.UI_BUTTON_PRESSED)
    def vs_rushb_ai(self, msg: pygame.event.Event) -> None:
        self.open_page("ChooseAIPlayerInfo")
        self.post(PageCallbackEvent("vs_rush_b_ai_clicked"))
        self.post(
            PageCallbackEvent(
                "send_player_info",
                payload=PlayerInfoPayload(self.player_1_info, self.player_1_path),
            )
        )
        self.close_self()

    @input_event_bind("go_back", pygame_gui.UI_BUTTON_PRESSED)
    def go_back(self, msg: pygame.event.Event) -> None:
        self.close_self()
        self.post(PageNavigationEvent([(PageNavigation.UNHIDE, "MainMenu")]))

    @callback_event_bind("send_player_info")
    def _set_player_info(self, event: PageCallbackEvent) -> None:
        assert isinstance(event.payload, PlayerInfoPayload)
        self.player_1_info = event.payload.player_1_info
        self.player_1_path = event.payload.player_1_path

    # endregion
