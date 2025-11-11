from ....entities.rodents.support import Quartermaster
from ...squeak import Squeak, SqueakType, rodent_placable_tile, summon_on_place

QUARTERMASTER = Squeak(
    name="Quartermaster",
    crumb_cost=19,
    squeak_type=SqueakType.RODENT,
    on_place=summon_on_place(Quartermaster),
    get_placable_tiles=rodent_placable_tile,
    rodent=Quartermaster,
)
