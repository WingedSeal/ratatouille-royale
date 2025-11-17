import importlib.resources as pkg_resources
import shutil
from platformdirs import user_config_dir, user_data_dir
from pathlib import Path
from . import assets

APP_NAME = "Ratroyale"

DATA_DIR_PATH = Path(user_data_dir(APP_NAME))
CONFIG_DIR_PATH = Path(user_config_dir(APP_NAME))

SPRITES_DIR_PATH = DATA_DIR_PATH / "sprites"
ICONS_DIR_PATH = DATA_DIR_PATH / "icons"
RRMAPS_DIR_PATH = DATA_DIR_PATH / "rrmaps"
TILESETS_DIR_PATH = DATA_DIR_PATH / "tilesets"
OTHER_IMAGES_PATH = DATA_DIR_PATH / "other_images"
RRSAVES_DIR_PATH = DATA_DIR_PATH / "saves"


def init_data() -> None:
    DATA_DIR_PATH.mkdir(parents=True, exist_ok=True)
    assets_root = pkg_resources.files(assets)

    for item in assets_root.iterdir():
        if item.name.startswith("__"):
            continue
        if not item.is_dir():
            raise Exception("A non-directory exists in assets directory.")
        source_name = item.name
        destination_path = DATA_DIR_PATH / source_name
        if destination_path.exists():
            continue

        with pkg_resources.as_file(item) as source_path:
            shutil.copytree(source_path, destination_path)

    RRSAVES_DIR_PATH.mkdir(parents=True, exist_ok=True)
