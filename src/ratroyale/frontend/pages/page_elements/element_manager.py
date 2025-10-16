from .element import ElementWrapper
from ratroyale.frontend.gesture.gesture_data import GestureData
from ratroyale.coordination_manager import CoordinationManager
from .spatial_component import Camera

from pygame import Surface
from pygame_gui import UIManager

from typing import TypeVar

T = TypeVar("T")


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
        self._element_collections: dict[str, dict[str, ElementWrapper]] = (
            {}
        )  # {element_type -> {element_id: element_obj}}
        self._flattened_collection: list[ElementWrapper] = []

        self._is_processing_input: bool = True
        self._camera: Camera = camera

    # region Collection Management

    def set_processing_status(self, is_processing_input: bool) -> None:
        self._is_processing_input = is_processing_input

    def create_collection(self, element_type: str) -> dict[str, ElementWrapper]:
        """Initializes a new collection for the given element type."""
        if element_type not in self._element_collections:
            self._element_collections[element_type] = {}
        return self._element_collections[element_type]

    def get_collection(self, element_type: str) -> dict[str, ElementWrapper]:
        """Retrieves the collection for the given element type, creating it if necessary."""
        if element_type not in self._element_collections:
            raise KeyError(f'"{element_type}" collection does not exist.')
        return self._element_collections[element_type]

    def add_element(self, element: ElementWrapper) -> None:
        """Adds an element to the specified collection, respecting parent-children relationships, and updates the flattened list."""
        try:
            collection = self.get_collection(element.grouping_name)
        except KeyError:
            collection = self.create_collection(element.grouping_name)

        if element.registered_name in collection:
            raise ValueError(
                f"Element with name '{element.registered_name}' already exists in collection '{element.grouping_name}'"
            )
        collection[element.registered_name] = element

        if element.element_parent:
            parent_id = element.element_parent.parent_registered_name
            parent_type = element.element_parent.parent_grouping_name

            parent_collection = self.get_collection(
                parent_type if parent_type else element.grouping_name
            )
            if parent_id in parent_collection:
                parent: ElementWrapper = parent_collection[parent_id]
                parent.add_child(element)
            else:
                raise ValueError(
                    f"Parent with id '{parent_id}' not found in collection '{parent_type}'"
                )
        self._flattened_collection.append(element)
        self._sort_flattened_by_z_order()

    def remove_element(self, element_type: str, key: str) -> None:
        """Removes an element and all its children from the collection and flattened list."""
        collection = self.get_collection(element_type)
        if key not in collection:
            return

        element: ElementWrapper = collection[key]

        # Remove from parent's children list if applicable
        if element.parent is not None:
            element.parent.children.remove(element)
            element.parent = None

        # Remove the element itself
        element.destroy()
        if element in self._flattened_collection:
            self._flattened_collection.remove(element)
        collection.pop(key)

        self._sort_flattened_by_z_order()

    def get_element_wrapper(
        self, registered_name: str, grouping_name: str
    ) -> ElementWrapper:
        group = self.get_collection(grouping_name)
        element = group[registered_name]
        if not element:
            raise KeyError("Element with the given registered name does not exist.")
        return element

    def clear_group_by_name(self, grouping_name: str) -> None:
        """Clears all elements from the specified collection.
        Also clears corresponding elements from the flattened list."""
        group = self.get_collection(grouping_name)
        for element in group.values():
            if grouping_name in self._element_collections:
                self._flattened_collection.remove(element)
            group.clear()
            self._sort_flattened_by_z_order()

    def clear_all(self) -> None:
        """Clears all collections and the flattened list."""
        self._element_collections.clear()
        self._flattened_collection.clear()

    def get_all_elements(self) -> dict[str, dict[str, ElementWrapper]]:
        return self._element_collections

    def get_flattened_elements(self) -> list[ElementWrapper]:
        return self._flattened_collection

    def _sort_flattened_by_z_order(self) -> None:
        self._flattened_collection.sort(
            key=lambda x: x.spatial_component.z_order, reverse=True
        )

    # endregion

    # region Rendering

    def update_all(self, time_delta: float) -> None:
        for element in reversed(self._flattened_collection):
            if element.visual_component:
                element.visual_component.animate(time_delta)

    def render_all(self, surface: Surface) -> None:
        """Default rendering: renders all elements in z-order."""
        for element in reversed(self._flattened_collection):
            element.render(surface)

    def render_collection(self, surface: Surface, element_type: str) -> None:
        """Render only elements of a specific type."""
        collection = self._element_collections.get(element_type, {})
        for element in sorted(
            collection.values(), key=lambda x: x.spatial_component.z_order, reverse=True
        ):
            element.render(surface)

    def render_elements(
        self, surface: Surface, keys: list[str], element_type: str
    ) -> None:
        """Render specific elements by key."""
        collection = self._element_collections.get(element_type, {})
        for key in keys:
            if key in collection:
                collection[key].render(surface)

    # endregion

    # region Processing Input

    def handle_gestures(self, gestures: list[GestureData]) -> list[GestureData]:
        """
        Dispatch a GestureData object to all non-gui elements.
        Elements then produces the corresponding event, which is
        handled by the page.
        """
        remaining_gestures: list[GestureData] = []

        for gesture in gestures:
            consumed = False

            for element in self._flattened_collection:
                if not element.interactable_component:
                    continue

                if element.handle_gesture(
                    gesture, self._is_processing_input, self._camera
                ):
                    consumed = True
                    break

            if not consumed:
                remaining_gestures.append(gesture)

        return remaining_gestures
