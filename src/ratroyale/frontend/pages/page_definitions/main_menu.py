import pygame
import pygame_gui

from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.page_token import *
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

from ..page_managers.base_page import Page

from ratroyale.backend.player_info.player_info import PlayerInfo
from ratroyale.event_tokens.payloads import PlayerInfoPayload
from ratroyale.event_tokens.page_token import PageCallbackEvent


# TODO: make helpers to make button registration easier
@register_page
class MainMenu(Page):
    def __init__(
        self, coordination_manager: CoordinationManager, camera: Camera
    ) -> None:
        self.player_info: PlayerInfo | None = None
        super().__init__(coordination_manager, theme_name="main_menu", camera=camera)

    def define_initial_gui(self) -> list[ElementWrapper]:
        """Return all GUI elements for the main menu page, auto-stacked vertically."""
        elements: list[ElementWrapper] = []

        # === Image ===
        banner_surface = pygame.Surface((100, 100))
        LIGHT_GRAY = (180, 180, 180)
        banner_surface.fill(LIGHT_GRAY)
        pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect(100, 100, 200, 100),
            image_surface=banner_surface,
            manager=self.gui_manager,
        )
        # === Right Corner ===
        player_info_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(-320, 20, 300, 55),
            manager=self.gui_manager,
            anchors={"right": "right", "top": "top"},
        )
        # Lvl
        player_level_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(5, 18, 50, 20),
            text="",
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="PlayerLevel", object_id="player_level_label"
            ),
            container=player_info_panel,
        )
        elements.append(
            ui_element_wrapper(player_level_label, "player_level_label", self.camera)
        )
        # Progress Bar
        progress_bar = pygame_gui.elements.UIProgressBar(
            relative_rect=pygame.Rect(55, 18, 120, 20),
            manager=self.gui_manager,
            container=player_info_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="ProgressBar", object_id="player_progress_bar"
            ),
        )
        elements.append(
            ui_element_wrapper(progress_bar, "player_progress_bar", self.camera)
        )

        # === cheese icon ===
        cheese_surface = pygame.Surface((40, 40))
        cheese_surface.fill((255, 220, 100))

        pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect(-50, 5, 40, 40),
            image_surface=cheese_surface,
            manager=self.gui_manager,
            container=player_info_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="cheeseIcon", object_id="cheese_icon"
            ),
            anchors={"left": "right", "top": "top"},
        )
        # === cheese text ===
        cheese_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(180, 3, 80, 50),
            text="999",
            manager=self.gui_manager,
            container=player_info_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="cheeseLabel", object_id="cheese_label"
            ),
        )
        elements.append(ui_element_wrapper(cheese_label, "cheese_label", self.camera))
        # === Player Name  ===
        player_name_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(-220, 80, 120, 25),
            text="",
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="PlayerNameLabel", object_id="player_name_label"
            ),
            anchors={"right": "right", "top": "top"},
        )
        elements.append(
            ui_element_wrapper(player_name_label, "player_name_label", self.camera)
        )

        button_specs = [
            ("start_button", "Start"),
            ("select_player_button", "Select Player"),
            ("forge_button", "Forge"),
            ("gacha_button", "Gacha"),
            ("quit_button", "Quit"),
        ]

        start_x = 100
        start_y = 210
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

    @input_event_bind("start_button", pygame_gui.UI_BUTTON_PRESSED)
    def on_start_click(self, msg: pygame.event.Event) -> None:
        self.post(PageNavigationEvent(action_list=[(PageNavigation.CLOSE_ALL, None)]))
        self.open_page("ChoosePlayer")
        assert self.player_info is not None
        self.post(
            PageCallbackEvent(
                "send_player_info",
                payload=PlayerInfoPayload(self.player_info, self.player_info_path),
            )
        )

    @input_event_bind("quit_button", pygame_gui.UI_BUTTON_PRESSED)
    def _on_quit_click(self, msg: pygame.event.Event) -> None:
        self.coordination_manager.stop_game()

    @input_event_bind("select_player_button", pygame_gui.UI_BUTTON_PRESSED)
    def _on_select_player_click(self, msg: pygame.event.Event) -> None:
        self.close_self()
        self.post(
            PageNavigationEvent(
                action_list=[
                    (PageNavigation.OPEN, "PlayerProfile"),
                ]
            )
        )

    @input_event_bind("gacha_button", pygame_gui.UI_BUTTON_PRESSED)
    def _on_open_gacha_click(self, msg: pygame.event.Event) -> None:
        self.close_self()
        self.post(
            PageNavigationEvent(
                action_list=[
                    (PageNavigation.OPEN, "GachaPage"),
                ]
            )
        )

    # endregion

    @callback_event_bind("set_player_info")
    def _set_player_info(self, event: PageCallbackEvent) -> None:
        assert isinstance(event.payload, PlayerInfoPayload)
        self.player_info = event.payload.player_info
        self.player_info_path = event.payload.path
        self._element_manager.get_element("player_name_label").get_interactable(
            pygame_gui.elements.UILabel
        ).set_text(event.payload.path.stem)
        self._element_manager.get_element("player_level_label").get_interactable(
            pygame_gui.elements.UILabel
        ).set_text(f"Level: {self.player_info.get_level()}")
        exp_leftover, exp_required_in_this_level = self.player_info.get_exp_progress()
        progress_bar = self._element_manager.get_element(
            "player_progress_bar"
        ).get_interactable(pygame_gui.elements.UIProgressBar)
        progress_bar.set_current_progress(
            exp_leftover * 100 / exp_required_in_this_level
        )
        self._element_manager.get_element("cheese_label").get_interactable(
            pygame_gui.elements.UILabel
        ).set_text(f"{self.player_info.cheese}")
