from ....entities.rodents.tank import Cracker
from ...squeak import Squeak, RodentSqueakInfo, rodent_placable_tile, summon_on_place

CRACKER = Squeak(
    name="Cracker",
    crumb_cost=19,
    on_place=summon_on_place(Cracker),
    get_placable_tiles=rodent_placable_tile,
    squeak_info=RodentSqueakInfo(Cracker),
)
