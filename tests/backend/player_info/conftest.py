import pytest

from ratroyale.backend.player_info.player_info import PlayerInfo
from ratroyale.backend.player_info.squeaks.rodents.vanguard import TAIL_BLAZER


@pytest.fixture
def example_player_info() -> PlayerInfo:
    return PlayerInfo(
        {TAIL_BLAZER: 5},
        [{TAIL_BLAZER: 5}],
        [{TAIL_BLAZER: 5}],
        selected_squeak_set_index=0,
    )
