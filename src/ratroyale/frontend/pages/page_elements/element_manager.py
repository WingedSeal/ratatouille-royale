from .element_builder import ElementConfig, create_element, ParentIdentity
from .element import Element
from ratroyale.frontend.gesture.gesture_data import GestureData
from ratroyale.coordination_manager import CoordinationManager

from pygame_gui import UIManager
from pygame_gui.core import UIElement, ObjectID
from pygame import Surface

from typing import TypeVar, Type, Optional

T = TypeVar("T")

class ElementManager:
    """
    Manages collections of elements grouped by element type string.
    Each type can have its own key-element structure.
    """
    def __init__(self, ui_manager: UIManager, coordination_manager: CoordinationManager) -> None:
        self.ui_manager = ui_manager
        self.coordination_manager = coordination_manager
        self._element_collections: dict[str, dict[str, Element]] = {} # {element_type -> {element_id: element_obj}}
        self._flattened_collection: list[Element] = []

        self._gui_element_collection: dict[str, UIElement] = {}

    # region Collection Management

    def create_collection(self, element_type: str) -> None:
        """Initializes a new collection for the given element type."""
        if element_type not in self._element_collections:
            self._element_collections[element_type] = {}

    def get_collection(self, element_type: str) -> dict:
        """Retrieves the collection for the given element type, creating it if necessary."""
        if element_type not in self._element_collections:
            self.create_collection(element_type)
        return self._element_collections[element_type]

    def add_element(
            self, 
            element_type: str, 
            key: str, 
            element: Element, 
            parent_identity: ParentIdentity | None
            ) -> None:
        """Adds an element to the specified collection, respecting parent-children relationships, and updates the flattened list."""
        collection = self.get_collection(element_type)
        if key in collection:
            raise ValueError(f"Element with key '{key}' already exists in collection '{element_type}'")
        collection[key] = element
        # print(f"Added element '{key}' to collection '{element_type}'")

        if parent_identity:
            parent_id = parent_identity.parent_id
            parent_type = parent_identity.parent_type
            offset = parent_identity.offset

            parent_collection = self.get_collection(parent_type if parent_type else element_type)
            if parent_id in parent_collection:
                parent: Element = parent_collection[parent_id]
                parent.add_child(element, offset)
                print(f"Set parent of element '{key}' to '{parent_id}'")
            else:
                raise ValueError(f"Parent with id '{parent_id}' not found in collection '{parent_type}'")
        self._flattened_collection.append(element)
        self._sort_flattened_by_z_order()

    def remove_element(self, element_type: str, key: str) -> None:
        """Removes an element and all its children from the collection and flattened list."""
        collection = self.get_collection(element_type)
        if key not in collection:
            return

        element: Element = collection[key]

        # Remove from parent's children list if applicable
        if element.parent is not None:
            element.parent.children.remove(element)
            element.parent = None

        # Remove the element itself
        element.destroy_visual()
        if element in self._flattened_collection:
            self._flattened_collection.remove(element)
        collection.pop(key)

        self._sort_flattened_by_z_order()

    def add_gui_element(self, gui_element: UIElement, registered_name: str) -> None:
        """
        Adds a GUI element to the collection, with the appropriate name for management.
        Note that this name should, but doesn't necessarily have to be the same as the actual
        object_id used internally by gui_element. \n
        i.e. the registered name and the event callback name can be different.
        """
        self._gui_element_collection[registered_name] = gui_element
        # print(f"Registered {gui_element} with name: {registered_name}")
    
    def get_gui_element(self, registered_name: str, cls: type[T]) -> T:
        element = self._gui_element_collection[registered_name]
        if not element:
            raise KeyError("Element with the given registered name does not exist.")
        if isinstance(element, cls):
            return element
        else:
            raise ValueError("The element type provided is incorrect.")


    def remove_gui_element(self, registered_name: str) -> None:
        """
        Remove the gui_element registered by this name.
        """
        removed = self._gui_element_collection.pop(registered_name)
        if removed:
            removed.kill()

    def clear_collection_of_type(self, element_type: str) -> None:
        """ Clears all elements from the specified collection. 
        Also clears corresponding elements from the flattened list."""
        if element_type in self._element_collections:
            collection = self._element_collections[element_type]
            for element in collection.values():
                if element in self._flattened_collection:
                    self._flattened_collection.remove(element)
            collection.clear()
            self._sort_flattened_by_z_order()

    def clear_all(self) -> None:
        """ Clears all collections and the flattened list."""
        self._element_collections.clear()
        self._flattened_collection.clear()
        self._gui_element_collection.clear()

    def create_element(self, cfg: ElementConfig) -> None:
        """Uses an external factory function to build the element from a config."""
        element = create_element(cfg, self.ui_manager)
        self.add_element(
            cfg.element_type, 
            cfg.id, 
            element, 
            cfg.parent_identity
            )

    def get_element(self, element_type: str, key: str) -> Element | None:
        """ Retrieves an element by type and key."""
        collection = self.get_collection(element_type)
        return collection[key] if key in collection else None

    def get_all_elements(self) -> dict[str, dict[str, Element]]:
        return self._element_collections
    
    def get_flattened_elements(self) -> list[Element]:
        return self._flattened_collection
    
    def _sort_flattened_by_z_order(self) -> None:
        self._flattened_collection.sort(key=lambda x: x.z_order, reverse=True)

    # endregion

    # region Rendering

    def render_all(self, surface: Surface) -> None:
        """Default rendering: renders all elements in z-order."""
        for element in reversed(self._flattened_collection):
            element.render(surface)

    def render_collection(self, surface: Surface, element_type: str) -> None:
        """Render only elements of a specific type."""
        collection = self._element_collections.get(element_type, {})
        for element in sorted(collection.values(), key=lambda x: x.z_order, reverse=True):
            element.render(surface)

    def render_elements(self, surface: Surface, keys: list[str], element_type: str) -> None:
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
                if not element.is_interactable:
                    continue

                if element.handle_gesture(gesture):
                    if element.is_blocking:
                        consumed = True
                        break

            if not consumed:
                remaining_gestures.append(gesture)

        return remaining_gestures
    
    



    
