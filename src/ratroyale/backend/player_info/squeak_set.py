from typing import TYPE_CHECKING

from .squeak import Squeak

if TYPE_CHECKING:
    from .player_info import PlayerInfo


class SqueakSet:
    deck_index: set[int]
    player_info: "PlayerInfo"

    def __init__(self, deck_index: set[int], player_info: "PlayerInfo") -> None:
        self.deck_index = deck_index
        self.player_info = player_info

    def get_new_deck(self) -> list[Squeak]:
        return [self.player_info.all_squeaks[index] for index in self.deck_index]
