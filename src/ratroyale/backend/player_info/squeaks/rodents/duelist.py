from ....entities.rodents.duelist import RatbertBrewbelly
from ...squeak import Squeak, SqueakType, rodent_placable_tile, summon_on_place

RATBERT_BREWBELLY = Squeak(
    name="Ratbert Brewbelly",
    crumb_cost=19,
    squeak_type=SqueakType.RODENT,
    on_place=summon_on_place(RatbertBrewbelly),
    get_placable_tiles=rodent_placable_tile,
    rodent=RatbertBrewbelly,
)
