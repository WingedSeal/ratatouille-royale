from ratroyale.coordination_manager import CoordinationManager

from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.payloads import FeaturePayload


from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.event_binder import (
    input_event_bind,
    callback_event_bind,
)
from ratroyale.frontend.pages.page_managers.page_registry import register_page

from ratroyale.frontend.pages.page_elements.element import (
    ElementWrapper,
    ui_element_wrapper,
)
from ..page_elements.spatial_component import Camera
from ratroyale.frontend.visual.screen_constants import SCREEN_SIZE

import pygame_gui
import pygame


@register_page
class InspectFeature(Page):
    def __init__(
        self, coordination_manager: CoordinationManager, camera: Camera
    ) -> None:
        super().__init__(
            coordination_manager,
            is_blocking=True,
            theme_name="inspect_feature",
            camera=camera,
            base_color=(0, 0, 0, 128),
        )

    def define_initial_gui(self) -> list[ElementWrapper]:

        gui_elements: list[ElementWrapper] = []

        panel_w, panel_h = 680, 460
        panel_x = (SCREEN_SIZE[0] - panel_w) // 2
        panel_y = (SCREEN_SIZE[1] - panel_h) // 2
        panel_element = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(panel_x, panel_y, panel_w, panel_h),
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="MainPanel", object_id="main_panel"
            ),
            anchors={"left": "left", "top": "top"},
        )
        panel_element_wrapper = ui_element_wrapper(
            panel_element, "main_panel", self.camera
        )
        gui_elements.append(panel_element_wrapper)

        close_button = ui_element_wrapper(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(-40, 12, 28, 28),
                text="x",
                manager=self.gui_manager,
                container=panel_element,
                object_id=pygame_gui.core.ObjectID(
                    class_id="CloseButton", object_id="close_button"
                ),
                anchors={
                    "right": "right",
                    "top": "top",
                },
            ),
            "close_button",
            self.camera,
        )
        gui_elements.append(close_button)

        title_label = ui_element_wrapper(
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(0, 56, 520, 32),
                text="Name / feature title",
                manager=self.gui_manager,
                container=panel_element,
                object_id=pygame_gui.core.ObjectID(
                    class_id="FeatureTitle", object_id="title"
                ),
                anchors={"centerx": "centerx", "top": "top"},
            ),
            "title",
            self.camera,
        )
        gui_elements.append(title_label)

        desc_box = ui_element_wrapper(
            pygame_gui.elements.UITextBox(
                html_text="<b>Description</b><br>"
                "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                relative_rect=pygame.Rect(20, 120, 640, 120),
                manager=self.gui_manager,
                container=panel_element,
                object_id=pygame_gui.core.ObjectID(
                    class_id="FeatureDesc", object_id="desc"
                ),
                anchors={
                    "left": "left",
                    "top": "top",
                },
            ),
            "desc",
            self.camera,
        )
        gui_elements.append(desc_box)

        portrait_surface = pygame.Surface((50, 200), flags=pygame.SRCALPHA)
        portrait_surface.fill((220, 220, 255))
        pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect(0, 280, 300, 150),
            image_surface=portrait_surface,
            manager=self.gui_manager,
            container=panel_element,
            anchors={"centerx": "centerx"},
        )

        return gui_elements

    @callback_event_bind("feature_data")
    def on_feature_data(self, msg: PageCallbackEvent) -> None:
        if msg.success and msg.payload:
            payload = msg.payload
            assert isinstance(payload, FeaturePayload)

            title_element = self._element_manager.get_element("title")
            title_label = title_element.get_interactable(pygame_gui.elements.UILabel)
            title_label.set_text(payload.feature_name)

            desc_element = self._element_manager.get_element("desc")
            desc_box = desc_element.get_interactable(pygame_gui.elements.UITextBox)
            desc_box.html_text = (
                f"<b>{payload.feature_name}</b><br>{payload.feature_description}"
            )
            desc_box.rebuild()

    @input_event_bind("close_button", pygame_gui.UI_BUTTON_PRESSED)
    def close_panel(self, msg: pygame.event.Event) -> None:
        self.post(
            PageNavigationEvent(action_list=[(PageNavigation.CLOSE, "InspectFeature")])
        )
