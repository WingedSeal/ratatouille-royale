from dataclasses import dataclass
from pygame_gui.core import UIElement
from typing import Literal
from ratroyale.frontend.pages.page_elements.element import Element
from ratroyale.event_tokens.payloads import Payload
from ratroyale.frontend.visual.asset_management.visual_component import (
    VisualComponent,
    ElementVisual,
    UIElementVisual,
)

GroupingName = Literal["UI_ELEMENT", "TILE", "ENTITY", "CARD"]
# more as needed


# TODO: what should Element provide?
# In addition to what is already defined in elements.py, an Element should also provide a Surface
# containing an image of itself. This could be a simple singular image, and can be extended to handle
# sprite animations via visual component later.
# TODO: revise ElementManager to consolidate element collections
# TODO: migrate all pages to test the system.
@dataclass
class ElementRegisterForm:
    """Wrapper for game elements (both custom and pygame_gui) to include custom payload & visual_component"""

    registered_name: str
    element: UIElement | Element
    grouping_name: GroupingName | None = None
    payload: Payload | None = None
    _visual_component: VisualComponent | None = None

    def setup_visual_component(self) -> None:
        """Create the correct visual component for the element."""
        if isinstance(self.element, UIElement):
            self._visual_component = UIElementVisual(self.element)
        elif isinstance(self.element, Element):
            self._visual_component = ElementVisual(self.element)
        else:
            raise TypeError(
                f"Provided element is neither of type Element nor UIElement: {type(self.element)}"
            )
