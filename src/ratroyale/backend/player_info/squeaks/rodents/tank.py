from ....entities.rodents.tank import Cracker
from ...squeak import Squeak, SqueakType, rodent_placable_tile, summon_on_place

CRACKER = Squeak(
    name="Cracker",
    crumb_cost=19,
    squeak_type=SqueakType.RODENT,
    on_place=summon_on_place(Cracker),
    get_placable_tiles=rodent_placable_tile,
    rodent=Cracker,
)
