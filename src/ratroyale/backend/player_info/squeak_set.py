from typing import TYPE_CHECKING

from .squeak import Squeak

if TYPE_CHECKING:
    from .player_info import PlayerInfo


class SqueakSet:
    deck_index: set[int]
    hands_index: set[int]
    player_info: "PlayerInfo"

    def __init__(
        self, deck_index: set[int], hands_index: set[int], player_info: "PlayerInfo"
    ) -> None:
        self.deck_index = deck_index
        self.player_info = player_info
        self.hands_index = hands_index

    def get_new_deck(self) -> list[Squeak]:
        return [self.player_info.all_squeaks[index] for index in self.deck_index]

    def get_deck_and_hand(self) -> tuple[list[Squeak], list[Squeak]]:
        return (
            [
                self.player_info.all_squeaks[index]
                for index in self.deck_index
                if index not in self.hands_index
            ],
            [self.player_info.all_squeaks[index] for index in self.hands_index],
        )
