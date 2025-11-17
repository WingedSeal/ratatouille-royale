import pytest

from ratroyale.backend.features.common import Lair
from ratroyale.backend.hexagon import OddRCoord
from ratroyale.backend.map import Map, heights_to_tiles
from ratroyale.backend.side import Side


@pytest.fixture
def example_map() -> Map:
    return Map(
        "Example Map",
        6,
        6,
        heights_to_tiles(
            [
                [1, 1, 1, 1, 1, None],
                [1, 2, 2, 1, 1, 1],
                [1, 2, 2, 3, 1, 1],
                [1, 1, 3, 3, 1, 1],
                [1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1],
            ]
        ),
        entities=[],
        features=[Lair([OddRCoord(0, 0)], 10, side=Side.RAT)],
    )
