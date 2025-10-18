from ....entities.rodents.duelist import (
    RatbertBrewbelly,
    SodaKabooma,
    Mortar,
    PeaPeaPoolPool,
)
from ...squeak import Squeak, SqueakType, rodent_placable_tile, summon_on_place

RATBERT_BREWBELLY = Squeak(
    name="Ratbert Brewbelly",
    crumb_cost=19,
    squeak_type=SqueakType.RODENT,
    on_place=summon_on_place(RatbertBrewbelly),
    get_placable_tiles=rodent_placable_tile,
    rodent=RatbertBrewbelly,
)
SODA_KABOOMA = Squeak(
    name="Soda Kabooma",
    crumb_cost=25,
    squeak_type=SqueakType.RODENT,
    on_place=summon_on_place(SodaKabooma),
    get_placable_tiles=rodent_placable_tile,
    rodent=SodaKabooma,
)
MORTAR = Squeak(
    name="Mortar",
    crumb_cost=32,
    squeak_type=SqueakType.RODENT,
    on_place=summon_on_place(Mortar),
    get_placable_tiles=rodent_placable_tile,
    rodent=Mortar,
)
PEA_PEA_POOL_POOL = Squeak(
    name="Pea Pea Pool Pool",
    crumb_cost=14,
    squeak_type=SqueakType.RODENT,
    on_place=summon_on_place(PeaPeaPoolPool),
    get_placable_tiles=rodent_placable_tile,
    rodent=PeaPeaPoolPool,
)
