from dataclasses import dataclass
from pathlib import Path

from ratroyale.backend.entities.rodents.vanguard import TailBlazer

ASSET_DIR = Path(__file__).resolve().parent.parent / "asset"


@dataclass
class SpritesheetMetadata:
    key: str
    path: Path
    sprite_size: tuple[int, int]
    animation_list: dict[str, list[int]]
    frame_rate: float = 60
    scale: tuple[float, float] = (1.0, 1.0)


SPRITE_METADATA_REGISTRY: dict[type, SpritesheetMetadata] = {
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
