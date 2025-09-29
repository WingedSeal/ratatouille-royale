from enum import Enum, auto


class Side(Enum):
    RAT = auto()
    MOUSE = auto()

    def other_side(self) -> "Side":
        if self == Side.RAT:
            return Side.MOUSE
        elif self == Side.MOUSE:
            return Side.RAT
        raise ValueError("Unreachable")

    @classmethod
    def from_int(cls, value: int) -> "Side | None":
        if value == 0:
            return None
        return cls(value)

    @classmethod
    def to_int(cls, value: "Side | None") -> int:
        if value is None:
            return 0
        return value.value
