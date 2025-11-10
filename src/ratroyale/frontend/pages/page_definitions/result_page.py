from ratroyale.coordination_manager import CoordinationManager

from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *

from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.page_registry import register_page
from ratroyale.frontend.pages.page_managers.event_binder import input_event_bind

from ratroyale.frontend.pages.page_elements.element import (
    ElementWrapper,
    ui_element_wrapper,
)
from ..page_elements.spatial_component import Camera

import pygame
import pygame_gui


@register_page
class Result(Page):
    def __init__(
        self,
        coordination_manager: CoordinationManager,
        camera: Camera,
    ) -> None:
        super().__init__(coordination_manager, camera, base_color=(0, 0, 0, 50))

    def define_initial_gui(self) -> list[ElementWrapper]:
        gui_elements: list[ElementWrapper] = []

        # === Main Panel ===
        panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, 0, 300, 350),
            manager=self.gui_manager,
            anchors={"centerx": "centerx", "centery": "centery"},
            object_id=pygame_gui.core.ObjectID(class_id="result_panel"),
        )
        panel_wrapper = ui_element_wrapper(panel, "main_panel", self.camera)
        gui_elements.append(panel_wrapper)

        # === Title Banner ===
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 20, 300, 60),
            text="YOU WIN!",
            manager=self.gui_manager,
            container=panel,
            object_id=pygame_gui.core.ObjectID(class_id="result_title"),
            anchors={"centerx": "centerx", "top": "top"},
        )

        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 90, 300, 40),
            text="EXP: +99",
            manager=self.gui_manager,
            container=panel,
            object_id=pygame_gui.core.ObjectID(class_id="result_score"),
            anchors={"centerx": "centerx"},
        )

        # === Reward Box ===
        reward_box = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, 130, 220, 70),
            manager=self.gui_manager,
            container=panel,
            object_id=pygame_gui.core.ObjectID(class_id="reward_box"),
            anchors={"centerx": "centerx"},
        )

        # === Currency icon ===
        cheese_surface = pygame.Surface((40, 40))
        cheese_surface.fill((255, 220, 100))

        pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect(-50, 10, 40, 40),
            image_surface=cheese_surface,
            manager=self.gui_manager,
            container=reward_box,
            object_id=pygame_gui.core.ObjectID(
                class_id="CurrencyIcon", object_id="currency_icon"
            ),
            anchors={"left": "right", "top": "top"},
        )

        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 10, 140, 50),
            text="+500",
            manager=self.gui_manager,
            container=reward_box,
            object_id=pygame_gui.core.ObjectID(class_id="reward_text"),
        )

        # === Bottom Buttons ===
        pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 250, 150, 60),
            text="OK",
            manager=self.gui_manager,
            container=panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="OKButton", object_id="ok_button"
            ),
            anchors={"centerx": "centerx"},
        )

        return gui_elements

    @input_event_bind("ok_button", pygame_gui.UI_BUTTON_PRESSED)
    def confirm_profile(self, msg: pygame.event.Event) -> None:
        self.close_self()
        CoordinationManager.put_message(
            PageNavigationEvent([(PageNavigation.OPEN, "MainMenu")])
        )
