from ....entities.rodents.vanguard import Tailblazer, Tailtrail
from ...squeak import Squeak, RodentSqueakInfo, rodent_placable_tile, summon_on_place

TAILBLAZER = Squeak(
    name="Tailblazer",
    crumb_cost=7,
    on_place=summon_on_place(Tailblazer),
    get_placable_tiles=rodent_placable_tile,
    squeak_info=RodentSqueakInfo(Tailblazer),
)

TAILTRAIL = Squeak(
    name="Tailtrail",
    crumb_cost=7,
    on_place=summon_on_place(Tailtrail),
    get_placable_tiles=rodent_placable_tile,
    squeak_info=RodentSqueakInfo(Tailtrail),
)
