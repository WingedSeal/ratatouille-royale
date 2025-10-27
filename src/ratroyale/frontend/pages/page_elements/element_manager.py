from .element import ElementWrapper
from ratroyale.frontend.gesture.gesture_data import GestureData
from ratroyale.coordination_manager import CoordinationManager
from .spatial_component import Camera
from .element_group import ElementGroup, HitTestPolicy

from pygame import Surface
from pygame_gui import UIManager
from ....event_tokens.payloads import Payload
from typing import TypeVar

T = TypeVar("T", bound="Payload")
U = TypeVar("U", bound="ElementWrapper")


class ElementManager:
    """
    Manages collections of elements grouped by element type string.
    Each type can have its own key-element structure.
    """

    def __init__(
        self,
        ui_manager: UIManager,
        coordination_manager: CoordinationManager,
        camera: Camera,
    ) -> None:
        self.ui_manager = ui_manager
        self.coordination_manager = coordination_manager

        self.element_groups: dict[str, ElementGroup] = {}
        self.flattened_element_groups: list[ElementGroup] = []
        self.element_to_group_mapping: dict[ElementWrapper, str] = {}

        self._is_processing_input: bool = True
        self._camera: Camera = camera

        self.master_group: ElementGroup = ElementGroup(
            group_name="_MASTER", max_selectable=None, camera=self._camera
        )

    # region Collection Management

    def set_processing_status(self, is_processing_input: bool) -> None:
        self._is_processing_input = is_processing_input

    def create_group(
        self,
        group_name: str,
        hittest_policy: HitTestPolicy = HitTestPolicy.REGULAR,
        hittest_priority: int = 1,
    ) -> ElementGroup:
        """Initializes a new group for the given element type."""
        if group_name not in self.element_groups:
            new_group = ElementGroup(group_name, self._camera)
            self.element_groups[group_name] = new_group
            self.flattened_element_groups.append(new_group)
            new_group.hittest_policy = hittest_policy
            new_group.hittest_priority = hittest_priority
            self.sort_group_by_hittest_priority()
        return self.element_groups[group_name]

    def get_group(self, group_name: str) -> ElementGroup:
        """Retrieves the collection for the given element type, creating it if necessary."""
        if group_name not in self.element_groups:
            print(f"group name {group_name} not already exists")
            group = self.create_group(group_name)
        else:
            group = self.element_groups[group_name]
        return group

    def add_element(self, element: ElementWrapper) -> None:
        """Adds an element to the master group and its specific group, respecting parent-children relationships."""
        self.master_group.add_element(element)

        group = self.get_group(element.grouping_name)
        group.add_element(element)
        self.element_to_group_mapping[element] = element.grouping_name

        # Handle parent-child relationship
        if element.parent_element:
            parent_name = element.parent_element
            try:
                parent_element = self.master_group.get_element(parent_name)
                parent_element.add_child(element)
            except KeyError:
                print(
                    f"Warning: parent element '{parent_name}' not found for '{element.registered_name}'"
                )

    def remove_element(
        self, registered_name: str, grouping_name: str | None = None
    ) -> ElementWrapper:
        """Removes an element and all its children from the master group and its group(s)."""
        removed_elem = self.master_group.remove_element(registered_name)

        # Determine group to remove from
        group = self.get_group(
            grouping_name if grouping_name else removed_elem.grouping_name
        )
        try:
            group.remove_element(registered_name)
        except KeyError:
            print(
                f"Warning: element '{registered_name}' not found in group '{group.group_name}'"
            )

        # Remove from parent's children list safely
        if removed_elem.parent and removed_elem in removed_elem.parent.children:
            removed_elem.parent.children.remove(removed_elem)
            removed_elem.parent = None

        # Recursively remove children
        for child in removed_elem.children.copy():
            self.remove_element(child.registered_name, child.grouping_name)

        # Clear the removed element's children list
        removed_elem.children.clear()

        return removed_elem

    def get_element(
        self, registered_name: str, grouping_name: str | None = None
    ) -> ElementWrapper:
        # If grouping name is not provided, it tries to look up in the master group.
        if not grouping_name:
            element = self.master_group.get_element(registered_name)
        else:
            group = self.get_group(grouping_name)
            element = group.get_element(registered_name)
        return element

    def clear_group_by_name(self, grouping_name: str) -> None:
        """Clears all elements from the specified collection.
        Also clears corresponding elements from the flattened list."""
        group = self.get_group(grouping_name)
        all_keys = group.clear()

        for keys in all_keys:
            self.master_group.remove_element(keys)

    def clear_all(self) -> None:
        """Clears all collections and the flattened list."""
        for group in self.element_groups.values():
            group.clear()
        self.element_groups.clear()
        self.master_group.clear()

    def get_all_elements(self) -> list[ElementWrapper]:
        if self.master_group._needs_resort:
            self.master_group._sort_flattened_by_z_order()
            self.master_group._needs_resort = False
        return self.master_group.flattened_elements_list

    def get_group_without_grouping_name(
        self, registered_name: str, grouping_name: str | None
    ) -> ElementGroup:
        if not grouping_name:
            element = self.get_element(registered_name, grouping_name)
            group = self.get_group(element.grouping_name)
        else:
            group = self.get_group(grouping_name)
        return group

    def toggle_element(
        self,
        registered_name: str,
        grouping_name: str | None = None,
        override_policy: bool = False,
    ) -> ElementWrapper | None:
        group = self.get_group_without_grouping_name(registered_name, grouping_name)
        return group.toggle_element(registered_name, override_policy)

    def select_element(
        self, registered_name: str, grouping_name: str | None = None
    ) -> ElementWrapper | None:
        group = self.get_group_without_grouping_name(registered_name, grouping_name)
        return group.select(registered_name)

    def deselect_element(
        self, registered_name: str, grouping_name: str | None = None
    ) -> ElementWrapper | None:
        group = self.get_group_without_grouping_name(registered_name, grouping_name)
        return group.deselect(registered_name)

    def deselect_all(self, grouping_name: str) -> list[ElementWrapper]:
        group = self.get_group(grouping_name)
        return group.deselect_all()

    def get_selected_elements(self, grouping_name: str) -> list[ElementWrapper]:
        group = self.get_group(grouping_name)
        return group.get_selected_elements()

    def set_max_selectable(self, group_name: str, amount: int | None) -> None:
        group = self.get_group(group_name)
        group.max_selectable = amount

    def get_payload_from_element(self, registered_name: str, cls: type[T]) -> T:
        element = self.get_element(registered_name)
        return element.get_payload(cls)

    def get_element_with_typecheck(self, registered_name: str, cls: type[U]) -> U:
        element = self.get_element(registered_name)
        if isinstance(element, cls):
            return element
        else:
            raise TypeError(
                f"Element {registered_name} is of type {type(element).__name__}, not {cls}."
            )

    def set_group_hittest_priority(self, group_name: str, new_priority: int) -> None:
        self.get_group(group_name).hittest_priority = new_priority

    def sort_group_by_hittest_priority(self) -> None:
        self.flattened_element_groups.sort(
            key=lambda x: x.hittest_priority, reverse=True
        )

    def get_all_groups(self) -> list[ElementGroup]:
        return self.flattened_element_groups

    # endregion

    # region Rendering

    def update_all(self, time_delta: float) -> None:
        for element in reversed(self.get_all_elements()):
            if element.visual_component:
                element.visual_component.animate(time_delta)

    def render_all(self, surface: Surface) -> None:
        """Default rendering: renders all elements in z-order."""
        for element in reversed(self.get_all_elements()):
            element.render(surface)

        self._camera.clear_dirty()

    # endregion

    # region Processing Input

    def handle_gestures(self, gestures: list[GestureData]) -> list[GestureData]:
        """
        Dispatch a GestureData object to all non-gui elements.
        Elements then produces the corresponding event, which is
        handled by the page.
        """
        remaining_gestures: list[GestureData] = gestures

        for element_group in self.get_all_groups():
            remaining_gestures = element_group.handle_gestures(
                remaining_gestures, self._is_processing_input
            )

        return remaining_gestures
