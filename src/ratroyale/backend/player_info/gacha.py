import random
from .squeaks.rodents.vanguard import TAIL_BLAZER
from .squeaks.rodents.tank import CRACKER
from .squeaks.rodents.duelist import (
    CLANKER,
    MORTAR,
    PEA_PEA_POOL_POOL,
    RAIL_RODENT,
    RATBERT_BREWBELLY,
    SODA_KABOOMA,
)
from .squeaks.rodents.specialist import MAYO, THE_ONE
from .squeaks.rodents.support import QUARTERMASTER
from .squeak import Squeak


CHEESE_PER_ROLL = 10
GACHA_POOL_WEIGHTS: dict[Squeak, float] = {
    TAIL_BLAZER: 1,
    MAYO: 0.5,
    CRACKER: 2,
    PEA_PEA_POOL_POOL: 1,
    RATBERT_BREWBELLY: 1,
    SODA_KABOOMA: 1,
    MORTAR: 1,
    RAIL_RODENT: 1,
    THE_ONE: 0.1,
    QUARTERMASTER: 0.5,
    CLANKER: 0.7,
}
"""Pool of all possible Squeak and its draw weight"""


def gacha_squeak(count: int = 1) -> list[Squeak]:
    return random.choices(
        list(GACHA_POOL_WEIGHTS.keys()), list(GACHA_POOL_WEIGHTS.values()), k=count
    )
