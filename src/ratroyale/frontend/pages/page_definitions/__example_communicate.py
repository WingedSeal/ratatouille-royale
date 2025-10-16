import pygame
import pygame_gui

from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.visual_token import *
from ratroyale.frontend.pages.page_elements.element_builder import UIRegisterForm
from ratroyale.frontend.pages.page_managers.event_binder import callback_event_bind
from ratroyale.frontend.pages.page_managers.page_registry import register_page

from ..page_managers.base_page import Page


@register_page
class TestCommunicate(Page):
    def __init__(self, coordination_manager: CoordinationManager) -> None:
        super().__init__(coordination_manager, is_blocking=False)

    def define_initial_gui(self) -> list[UIRegisterForm]:
        return [
            UIRegisterForm(
                "test_label",
                pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect(310, 350, 80, 30),
                    text="No numbers yet",
                    manager=self.gui_manager,
                    object_id=pygame_gui.core.ObjectID(
                        class_id="DemoLabel", object_id="label_id"
                    ),
                ),
            )
        ]

    @callback_event_bind("action_name")
    def receive(self, msg: PageCallbackEvent[int]) -> None:
        label = self._element_manager.get_gui_element(
            "test_label", pygame_gui.elements.UILabel
        )
        label.set_text(str(msg.payload))
