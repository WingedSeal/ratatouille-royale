from dataclasses import dataclass
from ..feature import Feature


@dataclass
class Lair(Feature):
    @staticmethod
    def FEATURE_ID() -> int:
        return 1

    @staticmethod
    def is_collision() -> bool:
        return True


@dataclass
class DeploymentZone(Feature):
    @staticmethod
    def FEATURE_ID() -> int:
        return 2

    @staticmethod
    def is_collision() -> bool:
        return False
