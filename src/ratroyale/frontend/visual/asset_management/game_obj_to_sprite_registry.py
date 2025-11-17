from dataclasses import dataclass
from collections import defaultdict
from ratroyale.backend.entities.rodents.vanguard import Tailblazer
from ratroyale.backend.entities.rodents.duelist import (
    RatbertBrewbelly,
    SodaKabooma,
)
from pathlib import Path
from ratroyale.backend.entity import Entity
from ratroyale.backend.player_info.squeak import Squeak
from ratroyale.backend.player_info.squeaks.rodents.duelist import (
    RATBERT_BREWBELLY,
    SODA_KABOOMA,
)
from ratroyale.backend.player_info.squeaks.rodents.vanguard import TAILBLAZER
from ratroyale.game_data import (
    ICONS_DIR_PATH,
    OTHER_IMAGES_PATH,
    SPRITES_DIR_PATH,
    TILESETS_DIR_PATH,
)


TYPICAL_TILE_SIZE = (64, 64)


@dataclass
class SpritesheetMetadata:
    key: str
    path: Path
    sprite_size: tuple[int, int]
    animation_list: dict[str, list[int]]
    frame_rate: float = 60
    scale: tuple[float, float] = (1.0, 1.0)


@dataclass
class TilesetMetadata:
    map_name: str
    path: Path
    sprite_size: tuple[int, int]
    row: int
    col: int
    tile_count: int


DUMMY_TEXTURE_METADATA: SpritesheetMetadata = SpritesheetMetadata(
    "DUMMY",
    OTHER_IMAGES_PATH / "missingTexture.jpg",
    (749, 745),
    {"NONE": [0], "HURT": [0]},
    60,
)


SPRITE_METADATA_REGISTRY: dict[type[Entity], SpritesheetMetadata] = {
    Tailblazer: SpritesheetMetadata(
        "TAILBLAZER",
        SPRITES_DIR_PATH / "tailblazer.gif",
        (80, 80),
        {
            "IDLE": list(range(0, 10)),
            "HURT": list(range(11, 20)),
            "DIE": list(range(21, 30)),
        },
        60,
    ),
    RatbertBrewbelly: SpritesheetMetadata(
        "RATBERT_BREWBELLY",
        SPRITES_DIR_PATH / "ratbert_brewbelly.gif",
        (80, 80),
        {
            "IDLE": list(range(0, 10)),
            "HURT": list(range(11, 20)),
            "DIE": list(range(21, 30)),
        },
        60,
    ),
    SodaKabooma: SpritesheetMetadata(
        "SODA_KABOOMA",
        SPRITES_DIR_PATH / "soda_kabooma.gif",
        (80, 80),
        {
            "IDLE": list(range(0, 10)),
            "HURT": list(range(11, 20)),
            "DIE": list(range(21, 30)),
        },
        60,
    ),
}

SQUEAK_IMAGE_METADATA_REGISTRY: dict[Squeak, SpritesheetMetadata] = {
    TAILBLAZER: SpritesheetMetadata(
        "TAILBLAZER_SQUEAK",
        SPRITES_DIR_PATH / "tailblazer_squeak.png",
        (238, 150),
        {"NONE": [0]},
        60,
    ),
    RATBERT_BREWBELLY: SpritesheetMetadata(
        "RATBERT_BREWBELLY_SQUEAK",
        SPRITES_DIR_PATH / "ratbert_brewbelly_squeak.png",
        (238, 150),
        {"NONE": [0]},
        60,
    ),
    SODA_KABOOMA: SpritesheetMetadata(
        "RATBERT_BREWBELLY_SQUEAK",
        SPRITES_DIR_PATH / "soda_kabooma_squeak.png",
        (238, 154),
        {"NONE": [0]},
        60,
    ),
}

TILESET_MAP: dict[str, TilesetMetadata] = {
    "Starting Kitchen": TilesetMetadata(
        "Starting Kitchen",
        TILESETS_DIR_PATH / "starting-kitchen.png",
        (100, 100),
        row=10,
        col=8,
        tile_count=77,
    )
}

spritesheet_metadata_cache: dict[str, dict[int, SpritesheetMetadata]] = defaultdict(
    dict
)


def get_spritesheet_metadata(
    tileset_metadata: TilesetMetadata, tile_id: int
) -> SpritesheetMetadata:
    if tile_id > tileset_metadata.tile_count:
        raise ValueError("Invalid tile_id")
    if tile_id in spritesheet_metadata_cache[tileset_metadata.map_name]:
        return spritesheet_metadata_cache[tileset_metadata.map_name][tile_id]
    spritesheet_metadata = SpritesheetMetadata(
        f"{tileset_metadata.map_name}-{tile_id}",
        tileset_metadata.path,
        tileset_metadata.sprite_size,
        {"NONE": [tile_id - 1]},
    )
    spritesheet_metadata_cache[tileset_metadata.map_name][
        tile_id
    ] = spritesheet_metadata
    return spritesheet_metadata


FEATURE_SPRITE_METADATA: dict[int, SpritesheetMetadata] = {
    1: SpritesheetMetadata(
        "TEMP_LAIR",
        OTHER_IMAGES_PATH / "terrain32x32.png",
        (32, 32),
        {"NONE": [479]},
    ),
    2: SpritesheetMetadata(
        "TEMP_FEATURE",
        OTHER_IMAGES_PATH / "terrain32x32.png",
        (32, 32),
        {"NONE": [18]},
    ),
}

MISC_SPRITE_METADATA: dict[str, SpritesheetMetadata] = {
    "HealthIcon": SpritesheetMetadata(
        "HEALTH_ICON", ICONS_DIR_PATH / "HealthIcon.png", (20, 18), {"NONE": [0]}
    ),
    "MoveStaminaIcon": SpritesheetMetadata(
        "MOVE_STAMINA_ICON",
        ICONS_DIR_PATH / "MoveStaminaIcon.png",
        (16, 22),
        {"NONE": [0]},
    ),
}
