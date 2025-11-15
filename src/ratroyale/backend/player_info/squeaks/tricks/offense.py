from typing import TYPE_CHECKING, Iterable

from ....hexagon import OddRCoord
from ....entities.tricks.offense import Sundial
from ...squeak import Squeak, SqueakType, rodent_placable_tile, summon_on_place

if TYPE_CHECKING:
    from ....game_manager import GameManager


def sundial_placable_tiles(game_manager: "GameManager") -> Iterable[OddRCoord]:
    if all(
        lair.health == 1 for lair in game_manager.board.cache.lairs[game_manager.turn]
    ):
        return []
    return rodent_placable_tile(game_manager)


SUNDIAL = Squeak(
    name="Sundial",
    crumb_cost=30,
    squeak_type=SqueakType.TRICK,
    on_place=summon_on_place(Sundial),
    get_placable_tiles=sundial_placable_tiles,
    rodent=None,
)
