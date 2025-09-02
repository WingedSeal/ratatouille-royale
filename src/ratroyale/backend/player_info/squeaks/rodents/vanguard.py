from typing import TYPE_CHECKING

from ....entities.rodents.vanguard import TailBlazer
from ...squeak import Squeak, SqueakType,  summon_on_place


TAIL_BLAZER = Squeak(
    crumb_cost=7, squeak_type=SqueakType.RODENT, on_place=summon_on_place(TailBlazer))
