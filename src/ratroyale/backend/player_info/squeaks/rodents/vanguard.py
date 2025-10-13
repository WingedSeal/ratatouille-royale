from ....entities.rodents.vanguard import TailBlazer
from ...squeak import Squeak, SqueakType, rodent_placable_tile, summon_on_place

TAIL_BLAZER = Squeak(
    crumb_cost=7,
    squeak_type=SqueakType.RODENT,
    on_place=summon_on_place(TailBlazer),
    get_placable_tiles=rodent_placable_tile,
    rodent_or_trick=TailBlazer,
)
