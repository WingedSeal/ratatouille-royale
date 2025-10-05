from .element_builder import ElementType, ElementConfig, create_element
from .element import Element
from ratroyale.frontend.gesture.gesture_data import GestureData
from ratroyale.event_tokens.input_token import InputManagerEvent
from ratroyale.coordination_manager import CoordinationManager

from pygame_gui import UIManager
from pygame import Surface

class ElementManager:
    """
    Manages collections of elements grouped by ElementType.
    Each type can have its own key-element structure.
    """
    def __init__(self, ui_manager: UIManager, coordination_manager: CoordinationManager) -> None:
        self.ui_manager = ui_manager
        self.coordination_manager = coordination_manager
        self._collections: dict[ElementType, dict[str, Element]] = {}
        self._flattened_collection: list[Element] = []

    # region Collection Management

    def create_collection(self, element_type: ElementType) -> None:
        """Initializes a new collection for the given element type."""
        if element_type not in self._collections:
            self._collections[element_type] = {}

    def get_collection(self, element_type: ElementType) -> dict:
        """Retrieves the collection for the given element type, creating it if necessary."""
        if element_type not in self._collections:
            self.create_collection(element_type)
        return self._collections[element_type]

    def add_element(
            self, 
            element_type: ElementType, 
            key: str, 
            element: Element, 
            parent_id: tuple[str, ElementType] | None, 
            offset: tuple[int, int] | None = None
            ) -> None:
        """Adds an element to the specified collection, respecting parent-children relationships, and updates the flattened list."""
        collection = self.get_collection(element_type)
        if key in collection:
            raise ValueError(f"Element with key '{key}' already exists in collection '{element_type}'")
        collection[key] = element
        print(f"Added element '{key}' to collection '{element_type}'")

        if parent_id:
            parent_name, parent_type = parent_id
            parent_collection = self.get_collection(parent_type)
            if parent_name in parent_collection:
                parent: Element = parent_collection[parent_name]
                parent.add_child(element, offset)
                print(f"Set parent of element '{key}' to '{parent_name}'")
            else:
                raise ValueError(f"Parent with id '{parent_name}' not found in collection '{parent_type}'")
        self._flattened_collection.append(element)
        self._sort_flattened_by_z_order()

    def remove_element(self, element_type: ElementType, key: str) -> None:
        """ Removes an element from the specified collection and updates the flattened list."""
        collection = self.get_collection(element_type)
        if key in collection:
            element: Element = collection[key]
            if element in self._flattened_collection:
                element.destroy_visual()
                self._flattened_collection.remove(element)
            del collection[key]
            self._sort_flattened_by_z_order()

    def clear_collection(self, element_type: ElementType) -> None:
        """ Clears all elements from the specified collection. 
        Also clears corresponding elements from the flattened list."""
        if element_type in self._collections:
            collection = self._collections[element_type]
            for element in collection.values():
                if element in self._flattened_collection:
                    self._flattened_collection.remove(element)
            collection.clear()
            self._sort_flattened_by_z_order()

    def clear_all(self) -> None:
        """ Clears all collections and the flattened list."""
        self._collections.clear()
        self._flattened_collection.clear()

    def create_element(self, cfg: ElementConfig) -> None:
        """Uses an external factory function to build the element from a config."""
        element = create_element(cfg, self.ui_manager)
        self.add_element(cfg.element_type, cfg.id, element, cfg.parent_id, cfg.offset)

    def create_elements(self, cfgs: list[ElementConfig]) -> None:
        """ Creates multiple elements from a list of configs."""
        for cfg in cfgs:
            self.create_element(cfg)

    def get_element(self, element_type: ElementType, key: str) -> Element | None:
        """ Retrieves an element by type and key."""
        collection = self.get_collection(element_type)
        return collection[key] if key in collection else None

    def get_all_elements(self) -> dict[ElementType, dict[str, Element]]:
        return self._collections
    
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

    def render_collection(self, surface: Surface, element_type: ElementType) -> None:
        """Render only elements of a specific type."""
        collection = self._collections.get(element_type, {})
        for element in sorted(collection.values(), key=lambda x: x.z_order, reverse=True):
            element.render(surface)

    def render_elements(self, surface: Surface, keys: list[str], element_type: ElementType) -> None:
        """Render specific elements by key."""
        collection = self._collections.get(element_type, {})
        for key in keys:
            if key in collection:
                collection[key].render(surface)

    # endregion

    # region Processing Input

    def handle_inputs(self, gestures: list[GestureData]) -> list[GestureData]:
        """
        Dispatch a GestureData object to the appropriate Interactable(s).
        Interactable then produces the corresponding InputManagerEvent, which is
        handled by the page.
        """
        remaining_gestures: list[GestureData] = []
        
        for gesture in gestures:
            for element in self._flattened_collection:
                if element.is_interactable:
                    input_message: InputManagerEvent | None = element.process_gesture(gesture)
                    if input_message:
                        self.coordination_manager.put_message(input_message)

                        if element.is_blocking:
                            break
            else:
                remaining_gestures.append(gesture)

        return remaining_gestures
    



    
