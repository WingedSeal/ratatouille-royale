from dataclasses import dataclass
from ratroyale.backend.entities.rodents.vanguard import TailBlazer
from pathlib import Path
import sys

visual_folder = Path(__file__).parent.parent
sys.path.append(visual_folder.resolve().as_posix())

ASSET_DIR = visual_folder / "asset"


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
