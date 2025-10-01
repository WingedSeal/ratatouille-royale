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
        selected_squeak_set_index: int,
    ) -> None:
        self.all_squeaks = all_squeaks
        self.squeak_sets = [SqueakSet(squeak_set, self) for squeak_set in squeak_sets]
        self.selected_squeak_set_index = selected_squeak_set_index

    def get_squeak_set(self) -> SqueakSet:
        return self.squeak_sets[self.selected_squeak_set_index]

    @classmethod
    def from_file(cls, file: Path) -> "PlayerInfo":
        # TODO
        return cls([], [], 0)
