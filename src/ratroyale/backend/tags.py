from enum import Enum


class SkillTag(Enum):
    NO_TARGET_FEATURE = "no-target-feature"
    SELF_DEFEATED = "self-defeated"


class EntityTag(Enum):
    pass


class RodentClassTag(Enum):
    VANGUARD = "Vanguard"
    DUELIST = "Duelist"
    TANK = "Tank"
    SPECIALIST = "Specialist"
