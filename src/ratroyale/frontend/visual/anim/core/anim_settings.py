from enum import Enum, auto


class MoveAnimMode(Enum):
    MOVE_TO = auto()
    MOVE_BY = auto()


class ScaleMode(Enum):
    SCALE_TO_SIZE = auto()
    SCALE_BY_FACTOR = auto()


class HorizontalAnchor(Enum):
    LEFT = auto()
    MIDDLE = auto()
    RIGHT = auto()


class VerticalAnchor(Enum):
    UPPER = auto()
    MIDDLE = auto()
    LOWER = auto()


class SkewMode(Enum):
    """SKEW_TO: animates towards a target skew value
    SKEW_BY: animates relative to the current skew value
    """

    SKEW_TO = auto()
    SKEW_BY = auto()


class TimingMode(Enum):
    DURATION_PER_LOOP = auto()
    DURATION_IN_TOTAL = auto()
