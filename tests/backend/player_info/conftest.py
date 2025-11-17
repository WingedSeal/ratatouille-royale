import pytest

from ratroyale.backend.player_info.player_info import PlayerInfo
from ratroyale.backend.player_info.squeaks.rodents.vanguard import TAILBLAZER
from ratroyale.backend.player_info.squeaks.rodents.tank import CRACKER
from ratroyale.backend.player_info.squeaks.rodents.duelist import (
    PEA_PEA_POOL_POOL,
    MORTAR,
)


@pytest.fixture
def example_player_info() -> PlayerInfo:
    return PlayerInfo(
        {TAILBLAZER: 5, CRACKER: 2, PEA_PEA_POOL_POOL: 3, MORTAR: 1},
        [{TAILBLAZER: 5}],
        [{TAILBLAZER: 5}],
        selected_squeak_set_index=0,
        exp=0,
        cheese=0,
        is_progression_frozen=False,
    )
