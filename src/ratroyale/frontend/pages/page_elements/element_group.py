from .element import ElementWrapper
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import deque
from ratroyale.frontend.gesture.gesture_data import GestureData
from ratroyale.backend.hexagon import OddRCoord
from ratroyale.frontend.visual.asset_management.game_obj_to_sprite_registry import (
    TYPICAL_TILE_SIZE,
)
from ..page_elements.spatial_component import Camera
from ratroyale.event_tokens.payloads import TilePayload


class OverselectionPolicy(Enum):
    REMOVE_OLDEST = auto()
    PREVENT_NEW = auto()


class HitTestPolicy(Enum):
    REGULAR = auto()
    NO_HITTEST = auto()
    HEXGRID = auto()


@dataclass
class ElementGroup:
    group_name: str
    camera: Camera
    elements: dict[str, ElementWrapper] = field(default_factory=dict)
    flattened_elements_list: list[ElementWrapper] = field(default_factory=list)
    selected_ids: deque[str] = field(default_factory=deque)
    highlighted_ids: deque[str] = field(default_factory=deque)
    max_selectable: int | None = 1
    """Max number of selectable elements. None represents infinite selection"""
    max_highlightable: int | None = 1
    """Max number of highlightable elements. None represents infinite selection"""
    overselection_policy: OverselectionPolicy = OverselectionPolicy.REMOVE_OLDEST
    active: bool = True

    hittest_priority: int = 0
    hittest_policy: HitTestPolicy = HitTestPolicy.REGULAR
    hexgrid_pos_for_element: dict[OddRCoord, ElementWrapper] = field(
        default_factory=dict
    )
    _needs_resort = True

    def add_element(self, element: ElementWrapper) -> None:
        if element.registered_name in self.elements:
            raise KeyError(
                f"Element with name {element.registered_name} already in group {self.group_name}"
            )
        self.elements[element.registered_name] = element
        self.flattened_elements_list.append(element)

        if self.hittest_policy == HitTestPolicy.HEXGRID:
            # Very quick and dirty.
            if type(element.payload) is TilePayload:
                self.hexgrid_pos_for_element[element.payload.tile.coord] = element
        self._needs_resort = True

    def get_element(self, registered_name: str) -> ElementWrapper:
        try:
            result = self.elements[registered_name]
            return result
        except KeyError:
            raise KeyError(
                f"At get: the element with registered name: {registered_name} is not found in group {self.group_name}"
            )

    def get_all_elements(self) -> list[ElementWrapper]:
        return self.flattened_elements_list

    def get_selected_elements(self) -> list[ElementWrapper]:
        elements = []
        for name in self.selected_ids:
            elements.append(self.elements[name])

        return elements

    def remove_element(self, registered_name: str) -> ElementWrapper:
        try:
            result = self.elements.pop(registered_name)
        except KeyError:
            raise KeyError(
                f"At removal: the element with registered name: {registered_name} is not found in group {self.group_name}"
            )
        if registered_name in self.selected_ids:
            self.selected_ids.remove(registered_name)
        self.flattened_elements_list.remove(result)
        result.destroy()
        self._needs_resort = True
        return result

    def clear(self) -> list[str]:
        all_keys = list(self.elements.keys())
        self.elements.clear()
        self.flattened_elements_list.clear()
        return all_keys

    def set_active(self, active: bool) -> None:
        self.active = active

    def set_overselection_policy(
        self, overselection_policy: OverselectionPolicy
    ) -> None:
        self.overselection_policy = overselection_policy

    def toggle_element(
        self, registered_name: str, override_policy: bool = False
    ) -> ElementWrapper | None:
        """Toggles selection state of an element."""
        if registered_name in self.selected_ids:
            # Already selected -> deselect it
            return self.deselect(registered_name)
        else:
            # Not selected -> try selecting it
            return self.select(registered_name, override_policy=override_policy)

    def select(
        self, registered_name: str, override_policy: bool = False
    ) -> ElementWrapper | None:
        """Attempts to select an element, respecting selection limits and policy."""
        element = self.get_element(registered_name)

        # Already selected -> do nothing
        if registered_name in self.selected_ids:
            return element

        # Handle selection limit
        if self.max_selectable is not None and not override_policy:
            if len(self.selected_ids) >= self.max_selectable:
                if self.overselection_policy == OverselectionPolicy.REMOVE_OLDEST:
                    oldest_name = self.selected_ids.popleft()
                    try:
                        oldest_element = self.get_element(oldest_name)
                        oldest_element.on_deselect()
                    except KeyError:
                        pass
                elif self.overselection_policy == OverselectionPolicy.PREVENT_NEW:
                    return None

        # Activate the selection
        success = element.on_select()
        if success:
            self.selected_ids.append(registered_name)
        return element

    def deselect(self, registered_name: str) -> ElementWrapper | None:
        """Deselects an element if it's currently selected."""
        if registered_name not in self.selected_ids:
            return None

        try:
            element = self.get_element(registered_name)
        except KeyError:
            # Element was already removed
            self.selected_ids.remove(registered_name)
            return None

        self.selected_ids.remove(registered_name)
        element.on_deselect()
        return element

    def deselect_all(self) -> list[ElementWrapper]:
        # Copy to avoid modifying the deque/set while iterating
        element_list = []
        for registered_name in list(self.selected_ids):
            element = self.get_element(registered_name)
            element.on_deselect()
            element_list.append(element)
        self.selected_ids.clear()
        return element_list

    def _sort_flattened_by_z_order(self) -> None:
        self.flattened_elements_list.sort(
            key=lambda x: x.spatial_component.z_order, reverse=True
        )

    def handle_gestures(
        self, gestures: list[GestureData], is_processing_input: bool
    ) -> list[GestureData]:
        """
        Dispatch a GestureData object to all non-gui elements.
        Elements then produces the corresponding event, which is
        handled by the page.
        """
        if self._needs_resort:
            self._sort_flattened_by_z_order()
            self._needs_resort = False

        remaining_gestures: list[GestureData] = []

        if self.hittest_policy == HitTestPolicy.REGULAR:
            for gesture in gestures:
                consumed = False

                for element in self.flattened_elements_list:
                    consumed = element.handle_gesture(gesture, is_processing_input)
                    if consumed:
                        break

                if not consumed:
                    remaining_gestures.append(gesture)

            return remaining_gestures
        elif self.hittest_policy == HitTestPolicy.NO_HITTEST:
            return gestures
        elif self.hittest_policy == HitTestPolicy.HEXGRID:
            for gesture in gestures:
                consumed = False

                world_pos = self.camera.screen_to_world(*gesture.mouse_pos)
                odd_r_coord = OddRCoord.from_pixel(
                    *world_pos, TYPICAL_TILE_SIZE[0], is_bounding_box=True
                )
                if odd_r_coord in self.hexgrid_pos_for_element:
                    element = self.hexgrid_pos_for_element[odd_r_coord]
                else:
                    element = None

                consumed = (
                    element.handle_gesture(gesture, is_processing_input)
                    if element
                    else False
                )

                if not consumed:
                    remaining_gestures.append(gesture)

            return remaining_gestures
        else:
            raise ValueError("Hittest policy unrecognised.")
