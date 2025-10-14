from pathlib import Path
from typing import Final

from ratroyale.utils import DataPointer

from .squeak import Squeak
from .squeak_set import SqueakSet
from . import squeaks  # noqa


SAVE_FILE_EXTENSION = "save"
ENDIAN: Final = "big"


class PlayerInfo:
    all_squeaks: list[Squeak]
    squeak_sets: list[SqueakSet]
    selected_squeak_set_index: int

    _FORMAT_SPEC = """
    2 bytes for all_squeaks_length
    loop all_squeaks_length times {
        1 byte for squeak_name_length
        squeak_name_length bytes for squeak_name
    }
    1 bytes for squeak_sets_count
    loop squeak_sets_count times {
        1 byte for squeak_set_length
        loop squeak_set_length times {
            2 bytes for squeak_index
        }
    }
    loop squeak_sets_count times {
        loop 5 times {
            2 bytes for squeak_index
        }
    }
    2 bytes for select_squeak_set_index
    """

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
            for squeak_set, hand in zip(squeak_sets, hands, strict=True)
        ]
        self.selected_squeak_set_index = selected_squeak_set_index

    def get_squeak_set(self) -> SqueakSet:
        return self.squeak_sets[self.selected_squeak_set_index]

    @classmethod
    def load(cls, data: bytes) -> "PlayerInfo":
        data_pointer = DataPointer(data, ENDIAN)
        all_squeaks_length = data_pointer.get_byte(2)

        all_squeaks: list[Squeak] = []
        for _ in range(all_squeaks_length):
            squeak_name_length = data_pointer.get_byte()
            squeak_name = data_pointer.get_raw_bytes(squeak_name_length).decode()
            all_squeaks.append(Squeak.SQEAK_MAP[squeak_name])

        squeak_sets: list[set[int]] = []
        squeak_sets_count = data_pointer.get_byte()
        for _ in range(squeak_sets_count):
            squeak_set: list[int] = []
            squeak_set_length = data_pointer.get_byte()
            for _ in range(squeak_set_length):
                squeak_index = data_pointer.get_byte(2)
                squeak_set.append(squeak_index)
            squeak_sets.append(set(squeak_set))

        hands: list[set[int]] = []
        for _ in range(squeak_sets_count):
            hand: list[int] = []
            squeak_set_length = data_pointer.get_byte()
            for _ in range(squeak_set_length):
                squeak_index = data_pointer.get_byte(2)
                hand.append(squeak_index)
            hands.append(set(hand))

        selected_squeak_set_index = data_pointer.get_byte()

        return PlayerInfo(all_squeaks, squeak_sets, hands, selected_squeak_set_index)

    def save(self) -> bytes:
        data = bytearray()
        return bytes(data)

    @classmethod
    def from_file(cls, file_path: Path) -> "PlayerInfo | None":
        with file_path.open("rb") as file:
            data = file.read()
        try:
            return cls.load(data)
        except Exception:
            return None

    def to_file(self, file_path: Path) -> None:
        data = self.save()
        with file_path.open("wb") as file:
            file.write(data)
