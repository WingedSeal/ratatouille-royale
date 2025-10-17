from pathlib import Path
from typing import Final
from math import floor, sqrt

from ratroyale.utils import DataPointer

from .squeak import Squeak
from .squeak_set import SqueakSet, HAND_LENGTH
from . import squeaks  # noqa

SAVE_FILE_EXTENSION = "rrsave"
ENDIAN: Final = "big"


class PlayerInfo:
    all_squeaks: dict[Squeak, int]
    squeak_sets: list[SqueakSet]
    selected_squeak_set_index: int
    exp: int
    cheese: int

    _FORMAT_SPEC = """
    2 bytes for all_squeaks_length
    large_all_squeaks_length = 1 if all_squeaks_length > 255 else 0
    loop all_squeaks_length times {
        1 byte for squeak_name_length
        squeak_name_length bytes for squeak_name
        1 + large_all_squeaks_length bytes for squeak_count
    }
    1 bytes for squeak_sets_count
    loop squeak_sets_count times {
        1 byte for squeak_set_length
        loop squeak_set_length times 
            (1 + large_all_squeaks_length) bytes for squeak
            1 + large_all_squeaks_length bytes for squeak_count
        }
    }
    loop squeak_sets_count times {
        loop 5 times {
            (1 + large_all_squeaks_length) bytes for squeak
            1 + large_all_squeaks_length bytes for squeak_count
        }
    }
    1 byte for select_squeak_set_index
    4 bytes for exp
    4 bytes for cheese
    """

    def __init__(
        self,
        all_squeaks: dict[Squeak, int],
        squeak_sets: list[dict[Squeak, int]],
        hands: list[dict[Squeak, int]],
        *,
        selected_squeak_set_index: int,
        exp: int,
        cheese: int,
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
        self.exp = exp
        self.cheese = cheese

    def get_squeak_set(self) -> SqueakSet:
        return self.squeak_sets[self.selected_squeak_set_index]

    def get_level(self) -> int:
        """
        Level 1->2 EXP required: 100
        Level 2->3 EXP required: 200
        Level 3->4 EXP required: 300
        ...
        Level N->N+1 EXP required: 100*N

        Level 1->N EXP required: 50*N*(N-1)
        k EXP = Level (1+sqrt(1+0.08k))//2
        """
        return floor((1 + sqrt(1 + 0.08 * self.exp)) / 2)

    def get_exp_progress(self) -> tuple[int, int]:
        level = self.get_level()
        exp_leftover = self.exp - 50 * level * (level - 1)
        exp_required_in_this_level = 100 * level
        return exp_leftover, exp_required_in_this_level

    @classmethod
    def load(cls, data: bytes) -> "PlayerInfo":
        data_pointer = DataPointer(data, ENDIAN)
        all_squeaks_length = data_pointer.get_byte(2)

        large_all_squeaks_length = all_squeaks_length > 255

        all_squeaks: dict[Squeak, int] = {}
        for _ in range(all_squeaks_length):
            squeak_name_length = data_pointer.get_byte()
            squeak_name = data_pointer.get_raw_bytes(squeak_name_length).decode()
            squeak_count = data_pointer.get_byte(1 + large_all_squeaks_length)
            all_squeaks[(Squeak.SQEAK_MAP[squeak_name])] = squeak_count

        all_squeaks_list = list(all_squeaks.keys())

        squeak_sets: list[dict[Squeak, int]] = []
        squeak_sets_count = data_pointer.get_byte()
        for _ in range(squeak_sets_count):
            squeak_set: dict[Squeak, int] = {}
            squeak_set_length = data_pointer.get_byte()
            for _ in range(squeak_set_length):
                squeak = data_pointer.get_byte(1 + large_all_squeaks_length)
                squeak_count = data_pointer.get_byte(1 + large_all_squeaks_length)
                squeak_set[all_squeaks_list[squeak]] = squeak_count
            squeak_sets.append(squeak_set)

        hands: list[dict[Squeak, int]] = []
        for _ in range(squeak_sets_count):
            hand: dict[Squeak, int] = {}
            total_squeak_count = 0
            while total_squeak_count < 5:
                squeak = data_pointer.get_byte(1 + large_all_squeaks_length)
                squeak_count = data_pointer.get_byte(1 + large_all_squeaks_length)
                assert squeak_count > 0
                hand[all_squeaks_list[squeak]] = squeak_count
                total_squeak_count += squeak_count
            hands.append(hand)

        selected_squeak_set_index = data_pointer.get_byte()

        exp = data_pointer.get_byte(4)
        cheese = data_pointer.get_byte(4)

        return PlayerInfo(
            all_squeaks,
            squeak_sets,
            hands,
            selected_squeak_set_index=selected_squeak_set_index,
            exp=exp,
            cheese=cheese,
        )

    def save(self) -> bytes:
        data = bytearray()
        all_squeaks_length = len(self.all_squeaks)
        data.extend(all_squeaks_length.to_bytes(2, ENDIAN))
        large_all_squeaks_length = 1 if all_squeaks_length > 255 else 0
        for squeak, squeak_count in self.all_squeaks.items():
            encoded_squeak_name = squeak.name.encode()
            data.append(len(encoded_squeak_name))
            data.extend(encoded_squeak_name)
            data.append(squeak_count)

        all_squeaks_list = list(self.all_squeaks.keys())
        squeak_sets_count = len(self.squeak_sets)
        data.append(squeak_sets_count)
        for squeak_set in self.squeak_sets:
            squeak_set_length = len(squeak_set.deck)
            data.append(squeak_set_length)
            for squeak, squeak_count in squeak_set.deck.items():
                data.extend(
                    all_squeaks_list.index(squeak).to_bytes(
                        1 + large_all_squeaks_length, ENDIAN
                    )
                )
                data.extend(squeak_count.to_bytes(1 + large_all_squeaks_length))
        for squeak_set in self.squeak_sets:
            assert sum(squeak_set.hands.values()) == HAND_LENGTH
            for squeak, squeak_count in squeak_set.hands.items():
                data.extend(
                    all_squeaks_list.index(squeak).to_bytes(
                        1 + large_all_squeaks_length, ENDIAN
                    )
                )
                data.extend(squeak_count.to_bytes(1 + large_all_squeaks_length))

        data.append(self.selected_squeak_set_index)
        data.extend(self.exp.to_bytes(4, ENDIAN))
        data.extend(self.cheese.to_bytes(4, ENDIAN))

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
