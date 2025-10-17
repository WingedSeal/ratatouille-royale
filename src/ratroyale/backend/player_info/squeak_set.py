from typing import TYPE_CHECKING

from ..error import InvalidDeckError
from .squeak import Squeak

if TYPE_CHECKING:
    from .player_info import PlayerInfo

HAND_LENGTH = 5


class SqueakSet:
    deck: dict[Squeak, int]
    hands: dict[Squeak, int]
    player_info: "PlayerInfo"

    def __init__(
        self,
        deck: dict[Squeak, int],
        hands: dict[Squeak, int],
        player_info: "PlayerInfo",
    ) -> None:
        self.deck = deck
        self.player_info = player_info
        self.hands = hands

    def _validate_deck(self) -> None:
        if len(self.hands) != HAND_LENGTH:
            raise InvalidDeckError(f"hands's length is not {HAND_LENGTH}")
        for squeak_dict in (self.hands, self.deck):
            for squeak, count in squeak_dict.items():
                if squeak not in self.player_info.all_squeaks:
                    raise InvalidDeckError(
                        f"{squeak.name} doesn't exist in 'all_squeaks'"
                    )
                if count > (all_squeaks_count := self.player_info.all_squeaks[squeak]):
                    raise InvalidDeckError(
                        f"The set has {count} {squeak.name} but 'all_squeaks' only has {all_squeaks_count}"
                    )

    def get_new_deck(self) -> list[Squeak]:
        return [squeak for squeak, count in self.deck.items() for _ in range(count)]

    def get_deck_and_hand(self) -> tuple[list[Squeak], list[Squeak]]:
        return (
            [
                squeak
                for squeak, count in self.deck.items()
                for _ in range(count - self.hands[squeak])
            ],
            [squeak for squeak, count in self.hands.items() for _ in range(count)],
        )
