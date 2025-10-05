from typing import Type
from ratroyale.frontend.pages.page_managers.base_page import Page

_PAGE_REGISTRY: dict[str, Type[Page]] = {}

def register_page(cls: Type[Page]) -> Type[Page]:
    """
    Decorator that registers a Page subclass into the global registry.

    Example:
        @register_page
        class MainMenu(Page):
            ...
    """
    name = cls.__name__
    if name in _PAGE_REGISTRY:
        raise ValueError(f"Duplicate page registration: {name}")
    _PAGE_REGISTRY[name] = cls
    return cls


def resolve_page(page_name: str) -> Type[Page]:
    """
    Resolve a page class by name. Raises KeyError if not found.
    """
    try:
        return _PAGE_REGISTRY[page_name]
    except KeyError:
        raise KeyError(
            f"Page '{page_name}' not found in registry. "
            "Make sure it's imported and registered."
        )

def all_pages() -> list[str]:
    """Return a list of all registered page names (for debugging or introspection)."""
    return list(_PAGE_REGISTRY.keys())