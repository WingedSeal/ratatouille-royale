from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.input_token import InputManagerEvent
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *

from ratroyale.frontend.gesture.gesture_data import GestureType, to_event

from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.event_binder import input_event_bind
from ratroyale.frontend.pages.page_managers.page_registry import register_page

from ratroyale.frontend.pages.page_elements.element_builder import (
    ElementConfig,
    UIRegisterForm,
)

import pygame_gui
import pygame


@register_page
class GUIDemo(Page):
    def __init__(self, coordination_manager: CoordinationManager) -> None:
        super().__init__(coordination_manager, theme_name="gui_demo")

        gui_elements = []

        # region Slider + Label
        volume_slider_id = "volume_slider"
        volume_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(100, 350, 200, 30),
            start_value=50,
            value_range=(0, 100),
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="DemoSlider", object_id=volume_slider_id
            ),
        )
        gui_elements.append(UIRegisterForm(volume_slider_id, volume_slider))

        volume_label_id = "volume_label"
        volume_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(310, 350, 80, 30),
            text=f"{int(volume_slider.get_current_value())}%",
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="DemoLabel", object_id=volume_label_id
            ),
        )
        gui_elements.append(UIRegisterForm(volume_label_id, volume_label))
        # endregion

        # region Text Field + Label
        label_id = "text_output_label"
        label_element = UIRegisterForm(
            label_id,
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(50, 50, 300, 30),
                text="",
                manager=self.gui_manager,
            ),
        )
        gui_elements.append(label_element)

        input_id = "text_input_box"
        input_element = UIRegisterForm(
            input_id,
            pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect(50, 100, 300, 30),
                manager=self.gui_manager,
                object_id=pygame_gui.core.ObjectID(
                    class_id="TextInput", object_id=input_id
                ),
            ),
        )
        gui_elements.append(input_element)
        # endregion

        # region Additional GUI Elements: Checkbox, Radio Buttons, Progress Bar

        # --- Checkbox ---
        enable_sound_id = "enable_sound_checkbox"
        enable_sound_checkbox = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect(400, 200, 200, 50),
            item_list=["Enable Sound"],
            manager=self.gui_manager,
            allow_multi_select=True,
            object_id=pygame_gui.core.ObjectID(
                class_id="DemoCheckbox", object_id=enable_sound_id
            ),
        )
        gui_elements.append(UIRegisterForm(enable_sound_id, enable_sound_checkbox))

        # --- Radio Buttons ---
        difficulty_radio_id = "difficulty_radio"
        difficulty_radio = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect(400, 260, 200, 80),
            item_list=["Easy", "Normal", "Hard"],
            manager=self.gui_manager,
            allow_multi_select=False,
            object_id=pygame_gui.core.ObjectID(
                class_id="DemoRadio", object_id=difficulty_radio_id
            ),
        )
        gui_elements.append(UIRegisterForm(difficulty_radio_id, difficulty_radio))

        # --- Progress Bar ---
        progress_bar_id = "progress_bar"
        progress_bar = pygame_gui.elements.UIProgressBar(
            relative_rect=pygame.Rect(400, 360, 200, 30),
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="DemoProgressBar", object_id=progress_bar_id
            ),
        )
        gui_elements.append(UIRegisterForm(progress_bar_id, progress_bar))

        button_progress_bar_id = "button_progress_bar"
        button_progress_bar = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(400, 390, 200, 50),
            text="Add progress",
            manager=self.gui_manager,
            object_id=pygame_gui.core.ObjectID(
                class_id="GUIDemoButton", object_id=button_progress_bar_id
            ),
        )
        gui_elements.append(UIRegisterForm(button_progress_bar_id, button_progress_bar))

        # endregion

        self.setup_gui_elements(gui_elements)

    # region Input Responses
    @input_event_bind("volume_slider", pygame_gui.UI_HORIZONTAL_SLIDER_MOVED)
    def on_slider_change(self, msg: pygame.event.Event) -> None:
        """Update the label as the slider moves."""
        input_element = self._element_manager.get_gui_element(
            "volume_slider", pygame_gui.elements.UIHorizontalSlider
        )
        label_element = self._element_manager.get_gui_element(
            "volume_label", pygame_gui.elements.UILabel
        )

        current_value = input_element.get_current_value()
        label_element.set_text(f"{current_value}%")
        print(f"Slider value: {current_value}%")

    @input_event_bind("text_input_box", pygame_gui.UI_TEXT_ENTRY_FINISHED)
    def _on_text_entered(self, event: pygame.event.Event) -> None:
        # Get input text
        input_element = self._element_manager.get_gui_element(
            "text_input_box", pygame_gui.elements.UITextEntryLine
        )
        label_element = self._element_manager.get_gui_element(
            "text_output_label", pygame_gui.elements.UILabel
        )

        text = input_element.get_text()
        label_element.set_text(text)

    @input_event_bind(
        "enable_sound_checkbox", pygame_gui.UI_SELECTION_LIST_NEW_SELECTION
    )
    def on_checkbox_change(self, event: pygame.event.Event) -> None:
        checkbox_element = self._element_manager.get_gui_element(
            "enable_sound_checkbox", pygame_gui.elements.UISelectionList
        )

        is_checked = "Enable Sound" in checkbox_element.get_multi_selection()
        print(f"Enable Sound: {is_checked}")

    @input_event_bind("difficulty_radio", pygame_gui.UI_SELECTION_LIST_NEW_SELECTION)
    def on_radio_change(self, event: pygame.event.Event) -> None:
        radio_element = self._element_manager.get_gui_element(
            "difficulty_radio", pygame_gui.elements.UISelectionList
        )

        selected = radio_element.get_single_selection()
        print(f"Selected difficulty: {selected}")

    @input_event_bind("button_progress_bar", pygame_gui.UI_BUTTON_PRESSED)
    def on_progress_change(self, event: pygame.event.Event) -> None:
        progress_button = self._element_manager.get_gui_element(
            "button_progress_bar", pygame_gui.elements.UIButton
        )
        progress_element = self._element_manager.get_gui_element(
            "progress_bar", pygame_gui.elements.UIProgressBar
        )

        progress_element.set_current_progress(
            min(progress_element.current_progress + 5, 100)
        )
        print(f"Progress bar value: {progress_element.current_progress}%")

    # endregion
