from ..feature import Feature


class Lair(Feature):
    @classmethod
    def FEATURE_ID(cls) -> int:
        return 1


class DeploymentZone(Feature):
    @classmethod
    def FEATURE_ID(cls) -> int:
        return 2
