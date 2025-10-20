import pygame
import pygame_gui

from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.visual_token import *
from ratroyale.frontend.pages.page_managers.event_binder import callback_event_bind
from ratroyale.frontend.pages.page_managers.page_registry import register_page


from ratroyale.frontend.pages.page_elements.element import (
    ElementWrapper,
    ui_element_wrapper,
)
from ratroyale.frontend.pages.page_elements.spatial_component import Camera
from ratroyale.event_tokens.payloads import (
    GameOverPayload,
)

from ..page_managers.base_page import Page


@register_page
class GameOver(Page):
    def __init__(
        self, coordination_manager: "CoordinationManager", camera: Camera
    ) -> None:
        super().__init__(
            coordination_manager,
            base_color=(0, 0, 0, 128),
            theme_name="pause_menu",
            camera=camera,
        )

    def define_initial_gui(self) -> list[ElementWrapper]:
        game_over_label = ui_element_wrapper(
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(200, 200, 400, 50),
                text="GAME OVER!!",
                manager=self.gui_manager,
                object_id=pygame_gui.core.ObjectID(
                    class_id="GameOverLabel", object_id="game_over_label"
                ),
            ),
            registered_name="game_over_label",
            camera=self.camera,
        )

        return [game_over_label]

    # --- Input Handlers ---
    @callback_event_bind("who_won")
    def _handle_game_over(self, msg: PageCallbackEvent) -> None:
        if msg.success and msg.payload:
            assert isinstance(msg.payload, GameOverPayload)
            payload = msg.payload
            winner = payload.victory_side

            game_over_panel_wrapper = self._element_manager.get_element(
                "game_over_label"
            )
            game_over_panel = game_over_panel_wrapper.get_interactable(
                pygame_gui.elements.UILabel
            )
            game_over_panel.set_text(
                f"GAME OVER!! {winner} is the winning side!!" + " (That's you! :) )"
                if payload.is_winner_from_first_turn_side
                else ""
            )
