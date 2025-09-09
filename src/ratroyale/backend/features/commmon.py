from dataclasses import dataclass
from typing import ClassVar
from ..feature import Feature


@dataclass
class Lair(Feature):
    @classmethod
    def FEATURE_ID(cls) -> int:
        return 1


@dataclass
class DeploymentZone(Feature):
    @classmethod
    def FEATURE_ID(cls) -> int:
        return 2
