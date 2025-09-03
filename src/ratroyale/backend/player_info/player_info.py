from pathlib import Path

from .squeak import Squeak
from .squeak_set import SqueakSet

SAVE_FILE_EXTENSION = "save"


class PlayerInfo:
    all_squeaks: list[Squeak]
    squeak_set: SqueakSet

    def __init__(self, all_squeaks: list[Squeak], squeak_set: SqueakSet) -> None:
        self.all_squeaks = all_squeaks
        self.squeak_set = squeak_set

    @classmethod
    def from_file(cls, file: Path) -> "PlayerInfo":
        # TODO
        return cls([], SqueakSet(deck=[]))
