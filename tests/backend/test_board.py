import pytest
from ratroyale.backend.entities.rodents.vanguard import TailBlazer
from ratroyale.backend.features.commmon import Lair
from ratroyale.backend.game_event import (
    EntityDamagedEvent,
    EntitySpawnEvent,
    FeatureDamagedEvent,
)
from ratroyale.backend.hexagon import OddRCoord
from ratroyale.backend.map import Map
from ratroyale.backend.board import Board
from ratroyale.backend.side import Side


@pytest.fixture
def empty_board(example_map: Map) -> Board:
    return Board(example_map)


@pytest.fixture
def example_board(empty_board: Board) -> Board:
    empty_board.add_entity(TailBlazer(OddRCoord(0, 0), Side.MOUSE))
    empty_board.event_queue.get_or_none()
    return empty_board


def test_cache(example_board: Board) -> None:
    assert type(example_board.cache.features[0]) == Lair
    assert type(example_board.cache.entities_with_hp[0]).name == "TailBlazer"


def test_add_entity(empty_board: Board) -> None:
    tail_blazer = TailBlazer(OddRCoord(0, 0), Side.MOUSE)
    empty_board.add_entity(tail_blazer)
    assert empty_board.event_queue.get_or_none() == EntitySpawnEvent(tail_blazer)


def test_get_tile(example_board: Board) -> None:
    tile = example_board.get_tile(OddRCoord(0, 0))
    assert tile is not None
    assert tile.entities[0].name == "TailBlazer"


def test_damage_entity(example_board: Board) -> None:
    tail_blazer = example_board.cache.entities_with_hp[0]
    assert tail_blazer.health is not None
    original_hp = tail_blazer.health
    damage = 4
    example_board.damage_entity(tail_blazer, damage)
    assert original_hp - tail_blazer.health == damage - tail_blazer.defense
    assert example_board.event_queue.get_or_none() == EntityDamagedEvent(
        tail_blazer, damage, damage - tail_blazer.defense
    )


def test_damage_feature(example_board: Board) -> None:
    lair = example_board.cache.lairs[Side.RAT][0]
    assert lair.health is not None
    original_hp = lair.health
    damage = 4
    example_board.damage_feature(lair, damage)
    assert original_hp - lair.health == damage - lair.defense
    assert example_board.event_queue.get_or_none() == FeatureDamagedEvent(
        lair, damage, damage - lair.defense
    )
