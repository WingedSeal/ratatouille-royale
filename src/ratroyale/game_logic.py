from enum import Enum, auto


class Side(Enum):
    PLAYER = auto()
    AI = auto()


class GameLogic:
    """
    Class responsible for main game logic, such as whose turn it is,
    how many crumbs each player has, etc.
    """

    turn: Side
    """Whose turn it currently is"""
    turn_count: int
    """How many turns it has been"""

    def __init__(self) -> None:
        self.turn = Side.PLAYER
        self.turn_count = 0
