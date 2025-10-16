import pygame
import pygame_gui

from ratroyale.backend.entity import Entity
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.visual_token import *
from ratroyale.frontend.pages.page_elements.element_builder import UIRegisterForm
from ratroyale.frontend.pages.page_managers.event_binder import (
    callback_event_bind,
    input_event_bind,
)
from ratroyale.frontend.pages.page_managers.page_registry import register_page

from ..page_managers.base_page import Page


@register_page
class EntityList(Page):
    def __init__(self, coordination_manager: CoordinationManager) -> None:
        super().__init__(coordination_manager, is_blocking=False)

    def define_initial_gui(self) -> list[UIRegisterForm]:
        entity_list_button_id = "entity_list_button"
        entity_list_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(700, 120, 80, 40),
            text="Entity",
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="EntityListButton", object_id=entity_list_button_id
            ),
        )
        return [UIRegisterForm(entity_list_button_id, entity_list_button)]

    @input_event_bind("entity_list_button", pygame_gui.UI_BUTTON_PRESSED)
    def _on_click(self, msg: pygame.event.Event) -> None:
        self.post(GameManagerEvent(game_action="entity_list"))

    @callback_event_bind("entity_list")
    def _create_entity_list(self, msg: PageCallbackEvent[list[Entity]]) -> None:
        button = self._element_manager.get_gui_element(
            "entity_list_button", pygame_gui.elements.UIButton
        )
        entity_list = msg.payload
        first_entity = entity_list[0].name if entity_list is not None else ""
        button.set_text(first_entity)
        pass
