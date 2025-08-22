import math
from random import shuffle

from .hexagon import OddRCoord
from .player_info.player_info import PlayerInfo
from .player_info.squeak import Squeak
from .map import Map
from .board import Board
from .side import Side

HAND_LENGTH = 5


def crumb_per_turn(turn_count: int):
    return min(math.ceil(turn_count / 4) * 10, 50)


class GameLogic:
    """
    Class responsible for main game logic, such as whose turn it is,
    how many crumbs each player has, etc.
    """

    turn: Side
    """Whose turn it currently is"""
    turn_count: int
    """How many turns it has been"""
    board: Board
    """Game board"""
    hands: dict[Side, list[Squeak]]
    """Player's hand. Always have length of {HAND_LENGTH}"""
    players_info: dict[Side, PlayerInfo]
    decks: dict[Side, list[Squeak]]
    crumbs: int
    """Crumbs of the current side"""
    first_turn: Side

    def __init__(self, map: Map, players_info: tuple[PlayerInfo, PlayerInfo], first_turn: Side) -> None:
        self.turn = first_turn
        self.turn_count = 1
        self.board = Board(map)
        self.hands = {
            Side.RAT: [self.draw_squeak(Side.RAT) for _ in range(HAND_LENGTH)],
            Side.MOUSE: [self.draw_squeak(Side.MOUSE) for _ in range(HAND_LENGTH)],
        }
        self.players_info = {
            first_turn: players_info[0],
            first_turn.other_side(): players_info[1]
        }
        self.decks = {
            Side.RAT: self.players_info[Side.RAT].squeak_set.deck.copy(),
            Side.MOUSE: self.players_info[Side.MOUSE].squeak_set.deck.copy()
        }

    def draw_squeak(self, side: Side) -> Squeak:
        """
        Get a squeak from a deck, spawn a new deck if it's empty
        """
        if self.decks[side]:
            return self.decks[side].pop()
        self.decks[side] = self.players_info[side].squeak_set.deck.copy()
        shuffle(self.decks[side])
        return self.decks[side].pop()

    def place_squeak(self, hand_index: int, coord: OddRCoord) -> bool:
        """
        Place squeak based on hand_index on the board
        """
        squeak = self.hands[self.turn][hand_index]
        if squeak.crumb_cost > self.crumbs:
            return False
        self.crumbs -= squeak.crumb_cost
        success = squeak.on_place(self.board, coord)
        if not success:
            return False
        self.hands[self.turn][hand_index] = self.draw_squeak(self.turn)
        return True

    def end_turn(self):
        self.turn = self.turn.other_side()
        if self.turn == self.first_turn:
            self.turn_count += 1
        self.crumbs = crumb_per_turn(self.turn_count)
