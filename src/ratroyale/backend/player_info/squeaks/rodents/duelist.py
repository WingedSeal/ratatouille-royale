from ....entities.rodents.duelist import (
    Clanker,
    Mortar,
    PeaPeaPoolPool,
    RailRodent,
    RatbertBrewbelly,
    SodaKabooma,
)
from ...squeak import (
    RodentSqueakInfo,
    Squeak,
    rodent_placable_tile,
    summon_on_place,
)

RATBERT_BREWBELLY = Squeak(
    name="Ratbert Brewbelly",
    crumb_cost=19,
    on_place=summon_on_place(RatbertBrewbelly),
    get_placable_tiles=rodent_placable_tile,
    squeak_info=RodentSqueakInfo(RatbertBrewbelly),
)
SODA_KABOOMA = Squeak(
    name="Soda Kabooma",
    crumb_cost=25,
    on_place=summon_on_place(SodaKabooma),
    get_placable_tiles=rodent_placable_tile,
    squeak_info=RodentSqueakInfo(SodaKabooma),
)
MORTAR = Squeak(
    name="Mortar",
    crumb_cost=32,
    on_place=summon_on_place(Mortar),
    get_placable_tiles=rodent_placable_tile,
    squeak_info=RodentSqueakInfo(Mortar),
)
PEA_PEA_POOL_POOL = Squeak(
    name="Pea Pea Pool Pool",
    crumb_cost=14,
    on_place=summon_on_place(PeaPeaPoolPool),
    get_placable_tiles=rodent_placable_tile,
    squeak_info=RodentSqueakInfo(PeaPeaPoolPool),
)
RAIL_RODENT = Squeak(
    name="Rail Rodent",
    crumb_cost=25,
    on_place=summon_on_place(RailRodent),
    get_placable_tiles=rodent_placable_tile,
    squeak_info=RodentSqueakInfo(RailRodent),
)
CLANKER = Squeak(
    name="Clanker",
    crumb_cost=20,
    on_place=summon_on_place(Clanker),
    get_placable_tiles=rodent_placable_tile,
    squeak_info=RodentSqueakInfo(Clanker),
)
