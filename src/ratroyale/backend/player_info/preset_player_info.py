from .player_info import PlayerInfo
from .squeak import Squeak
from .squeaks.rodents.vanguard import TAIL_BLAZER
from .squeaks.rodents.tank import CRACKER
from .squeaks.rodents.duelist import (
    PEA_PEA_POOL_POOL,
    MORTAR,
    RATBERT_BREWBELLY,
    SODA_KABOOMA,
)


def _make_ai_player_info(
    squeak_set: dict[Squeak, int], hand: dict[Squeak, int]
) -> PlayerInfo:
    return PlayerInfo(
        squeak_set,
        [squeak_set],
        [hand],
        selected_squeak_set_index=0,
        exp=0,
        cheese=0,
        is_progression_frozen=True,
    )


def get_default_player_info() -> PlayerInfo:
    return PlayerInfo(
        {TAIL_BLAZER: 4, PEA_PEA_POOL_POOL: 1},
        [{TAIL_BLAZER: 4, PEA_PEA_POOL_POOL: 1}],
        [{TAIL_BLAZER: 4, PEA_PEA_POOL_POOL: 1}],
        selected_squeak_set_index=0,
        exp=0,
        cheese=0,
        is_progression_frozen=False,
    )


AI_PLAYER_INFO = {
    "Balanced": _make_ai_player_info(
        {
            TAIL_BLAZER: 3,
            CRACKER: 3,
            MORTAR: 3,
            RATBERT_BREWBELLY: 3,
            SODA_KABOOMA: 2,
            PEA_PEA_POOL_POOL: 4,
        },
        {TAIL_BLAZER: 1, PEA_PEA_POOL_POOL: 2, MORTAR: 1, CRACKER: 1},
    )
}
