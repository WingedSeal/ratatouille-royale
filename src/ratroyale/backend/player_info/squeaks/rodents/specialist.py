from ....entities.rodents.specialist import Mayo
from ...squeak import Squeak, SqueakType, rodent_placable_tile, summon_on_place

MAYO = Squeak(
    name="Mayo",
    crumb_cost=7,
    squeak_type=SqueakType.RODENT,
    on_place=summon_on_place(Mayo),
    get_placable_tiles=rodent_placable_tile,
    rodent=Mayo,
)
