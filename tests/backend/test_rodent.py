import pytest

from ratroyale.backend.ai.random_ai import RandomAI
from ratroyale.backend.features.common import DeploymentZone
from ratroyale.backend.game_event import EntityDieEvent
from ratroyale.backend.game_manager import GameManager
from ratroyale.backend.player_info.player_info import PlayerInfo
from ratroyale.backend.player_info.squeak import Squeak
from ratroyale.backend.player_info.squeaks.rodents.duelist import (
    RATBERT_BREWBELLY,
)
from ratroyale.backend.hexagon import OddRCoord
from ratroyale.backend.map import Map, heights_to_tiles
from ratroyale.backend.side import Side


@pytest.fixture
def rodent_map() -> Map:
    return Map(
        "Rodent Map",
        2,
        1,
        heights_to_tiles([[1, 1]]),
        entities=[],
        features=[
            DeploymentZone([OddRCoord(0, 0)], None, side=Side.RAT),
            DeploymentZone([OddRCoord(1, 0)], None, side=Side.MOUSE),
        ],
    )


@pytest.mark.integration
@pytest.mark.parametrize("squeak", [RATBERT_BREWBELLY])
def test_rodents(rodent_map: Map, squeak: Squeak) -> None:
    game_manager = GameManager(
        rodent_map,
        players_info=(
            PlayerInfo(
                {squeak: 5},
                [{squeak: 5}],
                [{squeak: 5}],
                selected_squeak_set_index=0,
                exp=0,
                cheese=0,
                is_progression_frozen=True,
            ),
            PlayerInfo(
                {squeak: 5},
                [{squeak: 5}],
                [{squeak: 5}],
                selected_squeak_set_index=0,
                exp=0,
                cheese=0,
                is_progression_frozen=True,
            ),
        ),
        first_turn=Side.RAT,
    )
    ai = RandomAI(game_manager, Side.MOUSE)
    game_manager.crumbs = 1000
    game_manager.place_squeak(0, OddRCoord(0, 0))
    for _ in range(100):
        assert game_manager.turn == Side.RAT
        # Player Turn
        game_manager.end_turn()
        game_manager.crumbs = 1000
        # AI Turn
        ai.run_ai_and_update_game_manager()
        for event in game_manager.event_queue:
            if isinstance(event, EntityDieEvent):
                return
    assert False
