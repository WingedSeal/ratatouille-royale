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
class GachaPage(Page):
    def __init__(
        self, coordination_manager: CoordinationManager, camera: Camera
    ) -> None:
        super().__init__(coordination_manager, camera)

    def define_initial_gui(self) -> list[ElementWrapper]:
        gui_elements: list[ElementWrapper] = []

        # === BACK button ===
        back_button = ui_element_wrapper(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(10, 10, 120, 50),
                text="Back",
                manager=self.gui_manager,
                anchors={"left": "left", "top": "top"},
                object_id=pygame_gui.core.ObjectID(
                    class_id="BackButton", object_id="back_button"
                ),
            ),
            registered_name="back_button",
            camera=self.camera,
        )
        gui_elements.append(back_button)

        # === Currency text ===
        currency_label = ui_element_wrapper(
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(-130, 10, 80, 50),
                text="999",
                manager=self.gui_manager,
                anchors={"left": "right", "top": "top"},
                object_id=pygame_gui.core.ObjectID(
                    class_id="CurrencyLabel", object_id="currency_label"
                ),
            ),
            registered_name="back_button",
            camera=self.camera,
        )
        gui_elements.append(currency_label)

        # === Currency icon ===
        cheese_surface = pygame.Surface((40, 40))
        cheese_surface.fill((255, 220, 100))
        currency_icon = ui_element_wrapper(
            pygame_gui.elements.UIImage(
                relative_rect=pygame.Rect(-60, 15, 40, 40),
                image_surface=cheese_surface,
                manager=self.gui_manager,
                anchors={"left": "right", "top": "top"},
                object_id=pygame_gui.core.ObjectID(
                    class_id="CurrencyIcon", object_id="currency_icon"
                ),
            ),
            registered_name="currency_icon",
            camera=self.camera,
        )
        gui_elements.append(currency_icon)

        # === Image ===
        banner_surface = pygame.Surface((700, 400))
        LIGHT_GRAY = (180, 180, 180)
        banner_surface.fill(LIGHT_GRAY)
        image = ui_element_wrapper(
            pygame_gui.elements.UIImage(
                relative_rect=pygame.Rect(0, 0, 700, 400),
                image_surface=banner_surface,
                manager=self.gui_manager,
                anchors={"centerx": "centerx", "centery": "centery"},
                object_id=pygame_gui.core.ObjectID(class_id="Image", object_id="image"),
            ),
            registered_name="image",
            camera=self.camera,
        )
        gui_elements.append(image)

        # === 1 Draw button ===
        one_draw_button = ui_element_wrapper(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(-130, 520, 120, 50),
                text="1 Draw",
                manager=self.gui_manager,
                anchors={"centerx": "centerx"},
                object_id=pygame_gui.core.ObjectID(
                    class_id="OpenButton", object_id="one_draw_button"
                ),
            ),
            registered_name="one_draw_button",
            camera=self.camera,
        )
        gui_elements.append(one_draw_button)

        # === 10 Draws button ===
        ten_draws_button = ui_element_wrapper(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(130, 520, 120, 50),
                text="10 Draws",
                manager=self.gui_manager,
                anchors={
                    "centerx": "centerx",
                },
                object_id=pygame_gui.core.ObjectID(
                    class_id="OpenButton", object_id="ten_draws_button"
                ),
            ),
            registered_name="ten_draws_button",
            camera=self.camera,
        )
        gui_elements.append(ten_draws_button)

        return gui_elements

    @input_event_bind("back_button", pygame_gui.UI_BUTTON_PRESSED)
    def confirm_profile(self, msg: pygame.event.Event) -> None:
        self.close_self()
        CoordinationManager.put_message(
            PageNavigationEvent([(PageNavigation.OPEN, "MainMenu")])
        )
