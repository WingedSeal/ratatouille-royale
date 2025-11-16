from typing import TYPE_CHECKING, Iterable

from ....hexagon import OddRCoord
from ....entities.tricks.offense import Sundial
from ...squeak import (
    Squeak,
    TrickSqueakInfo,
    rodent_placable_tile,
    summon_on_place,
)

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
    on_place=summon_on_place(Sundial),
    get_placable_tiles=sundial_placable_tiles,
    squeak_info=TrickSqueakInfo(
        "Summon \"Sundial\".\
If not destroyed within 5 of enemy's turn, explode and set every of your lair's health to 1 \
and kill every entity in the field. (Cannot work if every lair's health is already 1)",
        (Sundial,),
    ),
)
