from typing import Type
from ratroyale.frontend.pages.page_managers.base_page import Page

import sys
from pathlib import Path
import importlib

# region Path Configuration

frontend_folder = Path(__file__).parent.parent
sys.path.append(str(frontend_folder.resolve()))

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
        try:
            importlib.import_module(module_path)
        except Exception as e:
            print(f"Failed to import {module_name}: {e}")


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


def resolve_theme_path(theme_name: str) -> Path:
    """
    Given a theme name (without extension), returns the absolute path
    to the corresponding JSON theme file in frontend/visual/gui_themes.

    Example:
        theme_name = "main_menu_theme"
        -> returns frontend/visual/gui_themes/main_menu_theme.json
    """
    # Determine project root (frontend/)
    BASE_DIR = (
        Path(__file__).resolve().parent.parent.parent
    )  # Adjust depending on file location
    theme_path = BASE_DIR / "visual" / "gui_themes" / f"{theme_name}.json"

    if not theme_path.exists():
        # raise FileNotFoundError(f"Theme JSON not found: {theme_path}")
        pass  # suppress for now

    return theme_path
