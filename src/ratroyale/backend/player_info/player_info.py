import hmac
import hashlib
from fernet import Fernet
from pathlib import Path
from typing import TYPE_CHECKING, Final
from math import exp, floor, sqrt

from ratroyale.backend.error import NotEnoughCrumbError
from ratroyale.utils import DataPointer

from .squeak import Squeak
from .gacha import CHEESE_PER_ROLL, gacha_squeak
from .squeak_set import SqueakSet, HAND_LENGTH
from . import squeaks as _squeaks  # noqa

if TYPE_CHECKING:
    from ..game_manager import GameManager

SAVE_FILE_EXTENSION = "rrsave"
ENDIAN: Final = "big"


def progression_curve(
    x: float, multiplier: float, estimated_linear_start: int, estimated_linear_end: int
) -> int:
    """y=floor(A(x/(x+B))(1-e^{-(x/C)^2}))"""
    return floor(
        multiplier
        * (x / (x + estimated_linear_start))
        * (1 - exp(-((x / estimated_linear_end) ** 2)))
    )


class PlayerInfo:
    all_squeaks: dict[Squeak, int]
    squeak_sets: list[SqueakSet]
    selected_squeak_set_index: int
    exp: int
    cheese: int
    is_progression_frozen: bool
    """Whether to not update exp and cheese upon game won. Used for AI."""

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
        is_progression_frozen: bool,
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
        self.is_progression_frozen = is_progression_frozen

    def get_squeak_set(self) -> SqueakSet:
        return self.squeak_sets[self.selected_squeak_set_index]

    def find_not_enough_squeak_in_sets(self, squeak: Squeak, count: int) -> int | None:
        """Return the first squeak set index that there's not enough squeak for removing.
        Return None if it can be savely removed. This already assumed there's enough squeak
        in the all_squeaks"""
        for i, squeak_set in enumerate(self.squeak_sets):
            if squeak not in squeak_set.deck:
                continue
            if squeak_set.deck[squeak] < count:
                return i
        return None

    def find_not_enough_squeak_in_hands(self, squeak: Squeak, count: int) -> int | None:
        """Return the first squeak set index that there's not enough squeak in hand for removing.
        Return None if it can be savely removed. This already assumed there's enough squeak
        in the all_squeaks and in squeak sets"""
        for i, squeak_set in enumerate(self.squeak_sets):
            if squeak not in squeak_set.hands:
                continue
            if squeak_set.hands[squeak] < count:
                return i
        return None

    def game_won(self, game_manager: "GameManager") -> None:
        if self.is_progression_frozen:
            return None
        self.cheese += progression_curve(game_manager.turn_count, 20, 20, 80)
        self.exp += progression_curve(game_manager.turn_count, 200, 20, 80)

    def game_lost(self, game_manager: "GameManager") -> None:
        if self.is_progression_frozen:
            return None
        self.cheese += progression_curve(game_manager.turn_count, 5, 20, 80)
        self.exp += progression_curve(game_manager.turn_count, 100, 20, 80)

    def gacha_squeak(self, count: int = 1) -> list[Squeak]:
        if self.cheese < count * CHEESE_PER_ROLL:
            raise NotEnoughCrumbError("Not enough chess to roll")
        self.cheese -= count * CHEESE_PER_ROLL
        squeaks = gacha_squeak(count)
        self._apply_gacha_squeak(squeaks)
        return squeaks

    def _apply_gacha_squeak(self, squeaks: list[Squeak]) -> None:
        for squeak in squeaks:
            self.all_squeaks[squeak] = self.all_squeaks.get(squeak, 0) + 1

    def get_level(self) -> int:
        """
        Level 1->2 EXP required: 100
        Level 2->3 EXP required: 110
        Level 3->4 EXP required: 120
        ...
        Level N->N+1 EXP required: 100 + 10*(N-1)

        Level 1->N EXP required: 5*N^2 + 85*N - 90
        k EXP = Level floor((-85 + sqrt(9025 + 20*k))/10)
        """
        if self.exp == 0:
            return 1

        return floor((-85 + sqrt(9025 + 20 * self.exp)) / 10)

    def get_exp_progress(self) -> tuple[int, int]:
        level = self.get_level()
        exp_to_current_level = (5 * level * level) + (85 * level) - 90
        exp_leftover = self.exp - exp_to_current_level
        exp_required_in_this_level = 100 + 10 * (level - 1)

        return exp_leftover, exp_required_in_this_level

    @classmethod
    def load(cls, data: bytes, *, is_progression_frozen: bool = False) -> "PlayerInfo":
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
            is_progression_frozen=is_progression_frozen,
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
    def from_file(
        cls, file_path: Path, *, is_progression_frozen: bool = False
    ) -> "PlayerInfo | None":
        with file_path.open("rb") as file:
            data = file.read()
        data = unprotect(data)
        try:
            return cls.load(data, is_progression_frozen=is_progression_frozen)
        except Exception:
            return None

    def to_file(self, file_path: Path) -> None:
        data = self.save()
        data = protect(data)
        with file_path.open("wb") as file:
            file.write(data)


SHA256_SIGNATURE_SIZE = 32
FERNET_KEY_SIZE = 44
"""Fernet key is base64-encoded 32 bytes = 44 bytes"""


def protect(data: bytes) -> bytes:
    key = Fernet.generate_key()
    assert len(key) == FERNET_KEY_SIZE
    cipher = Fernet(key)
    encrypted = cipher.encrypt(data)
    signature = hmac.new(key, encrypted, hashlib.sha256).digest()
    assert len(signature) == SHA256_SIGNATURE_SIZE
    return key + signature + encrypted


def unprotect(protected_data: bytes) -> bytes:
    key = protected_data[:FERNET_KEY_SIZE]
    signature = protected_data[
        FERNET_KEY_SIZE : FERNET_KEY_SIZE + SHA256_SIGNATURE_SIZE
    ]
    encrypted = protected_data[FERNET_KEY_SIZE + SHA256_SIGNATURE_SIZE :]
    expected_sig = hmac.new(key, encrypted, hashlib.sha256).digest()
    if not hmac.compare_digest(signature, expected_sig):
        raise ValueError("Data has been tampered with")
    cipher = Fernet(key)
    decrypted = cipher.decrypt(encrypted)
    assert isinstance(decrypted, bytes)
    return decrypted
