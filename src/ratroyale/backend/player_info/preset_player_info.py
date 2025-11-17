from typing import Final, Literal

from ratroyale.backend.player_info.squeaks.rodents.specialist import THE_ONE
from ratroyale.backend.player_info.squeaks.rodents.support import QUARTERMASTER
from ratroyale.backend.player_info.squeaks.tricks.offense import SUNDIAL
from .player_info import PlayerInfo
from .squeak import Squeak
from .squeaks.rodents.vanguard import TAILBLAZER, TAILTRAIL
from .squeaks.rodents.tank import CRACKER
from .squeaks.rodents.duelist import (
    CLANKER,
    PEA_PEA_POOL_POOL,
    MORTAR,
    RAIL_RODENT,
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
        {TAILBLAZER: 4, PEA_PEA_POOL_POOL: 1},
        [{TAILBLAZER: 4, PEA_PEA_POOL_POOL: 1}],
        [{TAILBLAZER: 4, PEA_PEA_POOL_POOL: 1}],
        selected_squeak_set_index=0,
        exp=0,
        cheese=0,
        is_progression_frozen=False,
    )


def get_demo_player_info() -> PlayerInfo:
    squeak_set = {
        TAILBLAZER: 1,
        TAILTRAIL: 2,
        PEA_PEA_POOL_POOL: 4,
        RATBERT_BREWBELLY: 3,
        CRACKER: 3,
        MORTAR: 2,
        RAIL_RODENT: 3,
        SODA_KABOOMA: 3,
        CLANKER: 1,
        QUARTERMASTER: 3,
        THE_ONE: 1,
        SUNDIAL: 1,
    }
    return PlayerInfo(
        squeak_set,
        [squeak_set],
        [
            {
                TAILBLAZER: 1,
                TAILTRAIL: 2,
                PEA_PEA_POOL_POOL: 1,
                RATBERT_BREWBELLY: 1,
            }
        ],
        selected_squeak_set_index=0,
        exp=0,
        cheese=0,
        is_progression_frozen=False,
    )


__ai_demo_player_info = get_demo_player_info()
__ai_demo_player_info.is_progression_frozen = True

AIPlayerInfo = Literal["Balanced", "Demo"]

AI_PLAYER_INFO: Final[dict[AIPlayerInfo, PlayerInfo]] = {
    "Balanced": _make_ai_player_info(
        {
            TAILBLAZER: 3,
            CRACKER: 3,
            MORTAR: 3,
            RATBERT_BREWBELLY: 3,
            SODA_KABOOMA: 2,
            PEA_PEA_POOL_POOL: 4,
        },
        {TAILBLAZER: 1, PEA_PEA_POOL_POOL: 2, MORTAR: 1, CRACKER: 1},
    ),
    "Demo": __ai_demo_player_info,
}
