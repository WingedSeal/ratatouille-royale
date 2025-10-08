from pathlib import Path


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
