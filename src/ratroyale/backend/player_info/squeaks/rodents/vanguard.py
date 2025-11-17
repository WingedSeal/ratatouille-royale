from ....entities.rodents.vanguard import Tailblazer
from ...squeak import Squeak, RodentSqueakInfo, rodent_placable_tile, summon_on_place

TAILBLAZER = Squeak(
    name="Tailblazer",
    crumb_cost=7,
    on_place=summon_on_place(Tailblazer),
    get_placable_tiles=rodent_placable_tile,
    squeak_info=RodentSqueakInfo(Tailblazer),
)
