from typing import TYPE_CHECKING, Iterable
from ....entities.rodents.specialist import Mayo, TheOne
from ...squeak import Squeak, SqueakType, rodent_placable_tile, summon, summon_on_place
from ....hexagon import OddRCoord

if TYPE_CHECKING:
    from ....game_manager import GameManager

MAYO = Squeak(
    name="Mayo",
    crumb_cost=7,
    squeak_type=SqueakType.RODENT,
    on_place=summon_on_place(Mayo),
    get_placable_tiles=rodent_placable_tile,
    rodent=Mayo,
)


def the_one_placable_tile(game_manager: "GameManager") -> Iterable[OddRCoord]:
    existing_the_one = game_manager.board.cache.the_ones[game_manager.turn]
    if existing_the_one is not None and existing_the_one.health != 0:
        return []
    return rodent_placable_tile(game_manager)


def the_one_on_place(game_manager: "GameManager", coord: OddRCoord) -> None:
    existing_the_one = game_manager.board.cache.the_ones[game_manager.turn]
    assert existing_the_one is None or existing_the_one.health == 0
    new_the_one = summon(game_manager, coord, TheOne)
    assert isinstance(new_the_one, TheOne)
    game_manager.board.cache.the_ones[game_manager.turn] = new_the_one


THE_ONE = Squeak(
    name="The One",
    crumb_cost=50,
    squeak_type=SqueakType.RODENT,
    on_place=the_one_on_place,
    get_placable_tiles=the_one_placable_tile,
    rodent=TheOne,
)
