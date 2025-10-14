from dataclasses import dataclass
from pygame_gui.core import UIElement
from typing import Literal
from ratroyale.frontend.pages.page_elements.element import ElementWrapper
from ratroyale.event_tokens.payloads import Payload
from ratroyale.frontend.visual.asset_management.visual_component import VisualComponent

GroupingName = Literal["UI_ELEMENT", "TILE", "ENTITY", "CARD"]
# more as needed


@dataclass
class ElementRegisterForm:
    """Wrapper for game elements (both custom and pygame_gui) to include custom payload & visual_component"""

    registered_name: str
    element: UIElement | ElementWrapper
    grouping_name: GroupingName
    payload: Payload | None = None
    visual_component: VisualComponent | None = None

    def destroy(self) -> None:
        if isinstance(self.element, UIElement):
            self.element.kill()  # type: ignore
