from .element import ElementWrapper
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import deque


class OverselectionPolicy(Enum):
    REMOVE_OLDEST = auto()
    PREVENT_NEW = auto()


@dataclass
class ElementGroup:
    group_name: str
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

    def add_element(self, element: ElementWrapper) -> None:
        if element.registered_name in self.elements:
            raise KeyError(
                f"Element with name {element.registered_name} already in group {self.group_name}"
            )
        self.elements[element.registered_name] = element
        self.flattened_elements_list.append(element)
        self._sort_flattened_by_z_order()

    def get_element(self, registered_name: str) -> ElementWrapper:
        result = self.elements[registered_name]
        if result:
            return result
        raise KeyError(
            f"At get: the element with registered name: {registered_name} is not found in group {self.group_name}"
        )

    def get_selected_elements(self) -> tuple[list[str], list[ElementWrapper]]:
        elements = []
        for name in self.selected_ids:
            elements.append(self.elements[name])

        return list(self.selected_ids), elements

    def remove_element(self, registered_name: str) -> ElementWrapper:
        result = self.elements.pop(registered_name)
        if not result:
            raise KeyError(
                f"At removal: the element with registered name: {registered_name} is not found in group {self.group_name}"
            )
        if registered_name in self.selected_ids:
            self.selected_ids.remove(registered_name)
        self.flattened_elements_list.remove(result)
        result.destroy()
        self._sort_flattened_by_z_order()
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
    ) -> None:
        """Toggles selection state of an element."""
        if registered_name in self.selected_ids:
            # Already selected -> deselect it
            self.deselect(registered_name)
        else:
            # Not selected -> try selecting it
            self.select(registered_name, override_policy=override_policy)

    def select(self, registered_name: str, override_policy: bool = False) -> bool:
        """Attempts to select an element, respecting selection limits and policy."""
        element = self.get_element(registered_name)

        # Already selected -> do nothing
        if registered_name in self.selected_ids:
            return False

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
                    return False

        # Activate the selection
        success = element.on_select()
        if success:
            self.selected_ids.append(registered_name)
        return success

    def deselect(self, registered_name: str) -> bool:
        """Deselects an element if it's currently selected."""
        if registered_name not in self.selected_ids:
            return False

        try:
            element = self.get_element(registered_name)
        except KeyError:
            # Element was already removed
            self.selected_ids.remove(registered_name)
            return False

        self.selected_ids.remove(registered_name)
        return element.on_deselect()

    def highlight(self, registered_name: str) -> bool:
        if self.max_highlightable is not None:
            if len(self.highlighted_ids) == self.max_highlightable:
                if self.overselection_policy == OverselectionPolicy.REMOVE_OLDEST:
                    oldest_name = self.highlighted_ids.popleft()
                    self.get_element(oldest_name).on_unhighlight()
                elif self.overselection_policy == OverselectionPolicy.PREVENT_NEW:
                    return False

        if registered_name not in self.highlighted_ids:
            self.highlighted_ids.append(registered_name)
            return self.get_element(registered_name).on_highlight()
        return False

    def unhighlight(self, registered_name: str) -> bool:
        if registered_name in self.highlighted_ids:
            self.highlighted_ids.remove(registered_name)
            return self.get_element(registered_name).on_unhighlight()
        return False

    def unhighlight_all(self) -> None:
        # Copy to avoid modifying the deque/set while iterating
        for registered_name in list(self.highlighted_ids):
            element = self.get_element(registered_name)
            element.on_unhighlight()
        self.highlighted_ids.clear()

    def deselect_all(self) -> None:
        # Copy to avoid modifying the deque/set while iterating
        for registered_name in list(self.selected_ids):
            element = self.get_element(registered_name)
            element.on_deselect()
        self.selected_ids.clear()

    def _sort_flattened_by_z_order(self) -> None:
        self.flattened_elements_list.sort(
            key=lambda x: x.spatial_component.z_order, reverse=True
        )
