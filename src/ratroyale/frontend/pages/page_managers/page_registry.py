import importlib
import sys
from pathlib import Path

from ratroyale.frontend.pages.page_managers.base_page import Page

# region Path Configuration

frontend_folder = Path(__file__).parent.parent
sys.path.append(frontend_folder.resolve().as_posix())

PAGES_FOLDER = frontend_folder / "page_definitions"
MODULE_PATH = "ratroyale.frontend.pages.page_definitions."

# endregion

_PAGE_REGISTRY: dict[str, type[Page]] = {}


def auto_import_pages() -> None:
    for py_file in PAGES_FOLDER.glob("*.py"):
        module_name = py_file.stem
        if module_name == "__init__":
            continue
        module_path = MODULE_PATH + module_name
        importlib.import_module(module_path)


def register_page(cls: type[Page]) -> type[Page]:
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


def resolve_page(page_name: str) -> type[Page]:
    """
    Resolve a page class by name. Raises KeyError if not found.
    """
    try:
        return _PAGE_REGISTRY[page_name]
    except KeyError:
        raise KeyError(
            f"Page '{page_name}' not found in registry. "
            "Make sure it's imported and registered, "
            "or make sure there are no code errors,"
            "or make sure the page class hasn't had it's name changed unexpectedly."
        )


def all_pages() -> list[str]:
    """Return a list of all registered page names (for debugging or introspection)."""
    return list(_PAGE_REGISTRY.keys())
