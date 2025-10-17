import pytest

from ratroyale.backend.player_info.player_info import PlayerInfo
from ratroyale.backend.player_info.squeaks.rodents.vanguard import TAIL_BLAZER
from ratroyale.backend.player_info.squeaks.rodents.tank import CRACKER
from ratroyale.backend.player_info.squeaks.rodents.duelist import (
    PEA_PEA_POOL_POOL,
    MORTAR,
)


@pytest.fixture
def example_player_info() -> PlayerInfo:
    return PlayerInfo(
        {TAIL_BLAZER: 5, CRACKER: 2, PEA_PEA_POOL_POOL: 3, MORTAR: 1},
        [{TAIL_BLAZER: 5}],
        [{TAIL_BLAZER: 5}],
        selected_squeak_set_index=0,
    )
