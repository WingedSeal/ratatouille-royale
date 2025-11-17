from pathlib import Path

from ratroyale.game_data import THEMES_PATH


def resolve_theme_path(theme_name: str) -> Path:
    """
    Given a theme name (without extension), returns the absolute path
    to the corresponding JSON theme file in frontend/visual/gui_themes.

    Example:
        theme_name = "main_menu_theme"
    """
    theme_path = THEMES_PATH / f"{theme_name}.json"

    if not theme_path.exists():
        pass

    return theme_path
