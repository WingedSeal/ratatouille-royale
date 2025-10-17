import pytest

from ratroyale.backend.ai.base_ai import BaseAI
from ratroyale.backend.ai.random_ai import RandomAI
from ratroyale.backend.ai.rushb_ai import RushBAI
from ratroyale.backend.features.common import DeploymentZone, Lair
from ratroyale.backend.game_manager import GameManager
from ratroyale.backend.hexagon import OddRCoord
from ratroyale.backend.map import Map, heights_to_tiles
from ratroyale.backend.player_info.player_info import PlayerInfo
from ratroyale.backend.player_info.squeaks.rodents.vanguard import TAIL_BLAZER
from ratroyale.backend.side import Side


@pytest.fixture
def small_map() -> Map:
    return Map(
        "Small Map",
        2,
        1,
        heights_to_tiles([[0, 0]]),
        entities=[],
        features=[
            Lair([OddRCoord(1, 0)], 1, side=Side.RAT),
            DeploymentZone([OddRCoord(0, 0)], side=Side.MOUSE),
        ],
    )


@pytest.mark.integration
@pytest.mark.parametrize("ai_type", [RandomAI, RushBAI])
def test_all_ai(small_map: Map, ai_type: type[BaseAI]) -> None:
    game_manager = GameManager(
        small_map,
        players_info=(
            PlayerInfo(
                {TAIL_BLAZER: 5},
                [{TAIL_BLAZER: 5}],
                [{TAIL_BLAZER: 5}],
                selected_squeak_set_index=0,
                exp=0,
                cheese=0,
                is_progression_frozen=True,
            ),
            PlayerInfo(
                {TAIL_BLAZER: 5},
                [{TAIL_BLAZER: 5}],
                [{TAIL_BLAZER: 5}],
                selected_squeak_set_index=0,
                exp=0,
                cheese=0,
                is_progression_frozen=True,
            ),
        ),
        first_turn=Side.RAT,
    )
    ai = ai_type(game_manager, Side.MOUSE)
    for _ in range(100):
        assert game_manager.turn == Side.RAT
        # Player Turn
        game_manager.end_turn()
        # AI Turn
        ai.run_ai_and_update_game_manager()
        if game_manager.game_over_event is not None:
            assert game_manager.game_over_event.victory_side == ai.ai_side
            return
    assert False
