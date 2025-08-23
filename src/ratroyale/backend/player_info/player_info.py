from pathlib import Path
from .squeak_set import SqueakSet

SAVE_FILE_EXTENSION = "save"


class PlayerInfo:
    squeak_set: SqueakSet

    def __init__(self, squeak_set: SqueakSet) -> None:
        self.squeak_set = squeak_set

    @classmethod
    def from_file(cls, file: Path) -> "PlayerInfo":
        # TODO
        return cls(SqueakSet())
