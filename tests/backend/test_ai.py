import pytest

from ratroyale.backend.ai.random_ai import RandomAI
from ratroyale.backend.features.commmon import DeploymentZone, Lair
from ratroyale.backend.game_event import GameOverEvent
from ratroyale.backend.hexagon import OddRCoord
from ratroyale.backend.map import Map, heights_to_tiles
from ratroyale.backend.player_info.player_info import PlayerInfo
from ratroyale.backend.side import Side
from ratroyale.backend.game_manager import GameManager
from ratroyale.backend.player_info.squeaks.rodents.vanguard import (
    TAIL_BLAZER,
)


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
def test_random_ai(small_map: Map) -> None:
    game_manager = GameManager(
        small_map,
        players_info=(
            PlayerInfo([TAIL_BLAZER] * 5, [{0, 1, 2, 3, 4}], [{0, 1, 2, 3, 4}], 0),
            PlayerInfo([TAIL_BLAZER] * 5, [{0, 1, 2, 3, 4}], [{0, 1, 2, 3, 4}], 0),
        ),
        first_turn=Side.RAT,
    )
    ai = RandomAI(game_manager, Side.MOUSE)
    for _ in range(100):
        # Player Turn
        game_manager.end_turn()
        # AI Turn
        ai.run_ai_and_update_game_manager()
        event = game_manager.event_queue.get_or_none()
        if isinstance(event, GameOverEvent):
            assert event.victory_side == ai.ai_side
            return
    assert False
