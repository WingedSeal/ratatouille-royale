import random

from .squeaks.tricks.offense import SUNDIAL
from .squeaks.rodents.vanguard import TAILBLAZER
import sys
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
    TAILBLAZER: 1,
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
    SUNDIAL: 0.1,
}
"""Pool of all possible Squeak and its draw weight"""


def gacha_squeak(seed: int, count: int = 1) -> tuple[list[Squeak], int]:
    random.seed(seed)
    result = random.choices(
        list(GACHA_POOL_WEIGHTS.keys()), list(GACHA_POOL_WEIGHTS.values()), k=count
    )
    new_seed = random.randrange(sys.maxsize)
    return result, new_seed
