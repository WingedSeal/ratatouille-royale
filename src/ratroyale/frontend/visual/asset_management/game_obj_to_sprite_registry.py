from dataclasses import dataclass
from ratroyale.backend.entities.rodents.vanguard import TailBlazer
from pathlib import Path
from ratroyale.backend.entities.rodent import Rodent

ASSET_DIR = Path(__file__).resolve().parent.parent / "asset"


@dataclass
class SpritesheetMetadata:
    key: str
    path: Path
    sprite_size: tuple[int, int]
    animation_list: dict[str, list[int]]
    frame_rate: float = 60
    scale: tuple[float, float] = (1.0, 1.0)


SPRITE_METADATA_REGISTRY: dict[type[Rodent], SpritesheetMetadata] = {
    TailBlazer: SpritesheetMetadata(
        "TAILBLAZER",
        ASSET_DIR / "starcatcher.png",
        (80, 80),
        {
            "IDLE": list(range(0, 10)),
            "HUNGRY": list(range(11, 20)),
            "DIE": list(range(21, 30)),
        },
        60,
    ),
}

SQUEAK_IMAGE_METADATA_REGISTRY: dict[type[Rodent], SpritesheetMetadata] = {
    TailBlazer: SpritesheetMetadata(
        "TAILBLAZER_CARD",
        ASSET_DIR / "snow_pea_card.png",
        (238, 150),
        {"NONE": [0]},
        60,
    )
}

# TODO: how does tile hold drawing data?
# Assuming all tiles are static, the animation list will be used to index into the spritesheet
TILE_SPRITE_METADATA: dict[int, SpritesheetMetadata] = {
    0: SpritesheetMetadata(
        "GRASS_TILE",
        ASSET_DIR / "terrain32x32.png",
        (32, 32),
        {"NONE": [156]},
    )
}
