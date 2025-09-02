from typing import TYPE_CHECKING

from ....entities.rodents.vanguard import TailBlazer
from ...squeak import Squeak, summon

if TYPE_CHECKING:
    from ....game_manager import GameManager
    from ....hexagon import OddRCoord


class TailBlazerSqueak(Squeak):
    def on_place(self, game_manager: "GameManager", coord: OddRCoord) -> bool:
        return summon(game_manager, coord, TailBlazer)
