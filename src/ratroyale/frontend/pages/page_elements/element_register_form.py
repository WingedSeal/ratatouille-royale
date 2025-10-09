from __future__ import annotations
from dataclasses import dataclass
from pygame_gui.core import UIElement
from ratroyale.event_tokens.payloads import Payload
from ratroyale.frontend.visual.asset_management.visual_component import VisualComponent


@dataclass
class ElementRegisterForm:
    """Wrapper for game elements (both custom and pygame_gui) to include custom payload & visual_component"""

    registered_name: str
    element: UIElement  # union CustomElement (to be implemented)
    grouping_name: str | None = None
    payload: Payload | None = None
    _visual_component: str | None = ""

    def setup_visual_component(self) -> None:
        # Depending on whethe the GUIRegisterForm is given a UIElement or a CustomElement,
        # this method will adjust accordingly to create the visual component.
        pass
