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


from ..page_managers.base_page import Page
from ratroyale.backend.map import Map


def _temp_get_map():  # type: ignore
    from ratroyale.backend.hexagon import OddRCoord
    from ratroyale.backend.features.common import DeploymentZone, Lair
    from ratroyale.backend.map import heights_to_tiles

    size = 10
    return Map(
        "Example Map",
        size,
        size,
        heights_to_tiles([[1 for i in range(size)] for i in range(size)]),
        entities=[],
        features=[
            Lair([OddRCoord(0, 0)], 10, side=Side.MOUSE),
            Lair([OddRCoord(size - 1, size - 1)], 10, side=Side.RAT),
            DeploymentZone(shape=[OddRCoord(0, 1), OddRCoord(1, 0)], side=Side.MOUSE),
            DeploymentZone(
                shape=[
                    OddRCoord(size - 2, size - 1),
                    OddRCoord(size - 1, size - 2),
                ],
                side=Side.RAT,
            ),
        ],
    )


# TODO: make helpers to make button registration easier
@register_page
class MainMenu(Page):
    def __init__(
        self, coordination_manager: CoordinationManager, camera: Camera
    ) -> None:
        super().__init__(coordination_manager, theme_name="main_menu", camera=camera)

    def define_initial_gui(self) -> list[ElementWrapper]:
        """Return all GUI elements for the main menu page, auto-stacked vertically."""
        elements: list[ElementWrapper] = []

        button_specs = [
            ("start_button", "Start"),
            ("select_player_button", "Select Player"),
            ("quit_button", "Quit"),
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

    @input_event_bind("start_button", pygame_gui.UI_BUTTON_PRESSED)
    def on_start_click(self, msg: pygame.event.Event) -> None:
        # map = Map.from_file(
        #     Path(__file__).parents[3] / "map_file/starting-kitchen.rrmap"
        # )
        map = _temp_get_map()  # type: ignore
        assert map
        self.post(
            GameManagerEvent(
                "start",
                BackendStartPayload(
                    map,
                    get_default_player_info(),
                    AI_PLAYER_INFO["Balanced"],
                    Side.RAT,
                    RushBAI,
                ),
            )
        )
        self.post(
            PageNavigationEvent(
                action_list=[
                    (PageNavigation.CLOSE_ALL, None),
                    (PageNavigation.OPEN, "GameBoard"),
                    (PageNavigation.OPEN, "GameInfoPage"),
                    (PageNavigation.OPEN, "PauseButton"),
                ]
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
                    (PageNavigation.OPEN, "SelectPlayerPage"),
                ]
            )
        )

    # endregion
