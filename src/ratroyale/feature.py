from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from .hexagon import OddRCoord


class FeatureId(Enum):
    DEPLOYMENT_ZONE_RAT = 1
    DEPLOYMENT_ZONE_MOUSE = 2


@dataclass
class Feature:
    shape: list[OddRCoord]
    feature_id: FeatureId
    image_path: Path | None
