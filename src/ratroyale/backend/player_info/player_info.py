from pathlib import Path

from .squeak import Squeak
from .squeak_set import SqueakSet

SAVE_FILE_EXTENSION = "save"


class PlayerInfo:
    all_squeaks: list[Squeak]
    squeak_sets: list[SqueakSet]
    selected_squeak_set_index: int

    def __init__(
        self,
        all_squeaks: list[Squeak],
        squeak_sets: list[set[int]],
        hands: list[set[int]],
        selected_squeak_set_index: int,
    ) -> None:
        self.all_squeaks = all_squeaks
        for i, (squeak_set, hand) in enumerate(zip(squeak_sets, hands)):
            for squeak in hand:
                if squeak not in squeak_set:
                    raise ValueError(
                        f"In set {i}, squeak [{squeak}] is in hand but not in deck."
                    )
        self.squeak_sets = [
            SqueakSet(squeak_set, hand, self)
            for squeak_set, hand in zip(squeak_sets, hands)
        ]
        self.selected_squeak_set_index = selected_squeak_set_index

    def get_squeak_set(self) -> SqueakSet:
        return self.squeak_sets[self.selected_squeak_set_index]

    @classmethod
    def from_file(cls, file: Path) -> "PlayerInfo":
        # TODO
        return cls([], [], [], 0)
