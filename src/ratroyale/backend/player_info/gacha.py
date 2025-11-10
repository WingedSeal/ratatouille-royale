import random
import sys
from .squeaks.rodents.vanguard import TAIL_BLAZER
from .squeaks.rodents.tank import CRACKER
from .squeaks.rodents.duelist import (
    MORTAR,
    PEA_PEA_POOL_POOL,
    RATBERT_BREWBELLY,
    SODA_KABOOMA,
)
from .squeaks.rodents.specialist import MAYO
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
}
"""Pool of all possible Squeak and its draw weight"""


def gacha_squeak(seed: int, count: int = 1) -> tuple[list[Squeak], int]:
    random.seed(seed)
    result = random.choices(
        list(GACHA_POOL_WEIGHTS.keys()), list(GACHA_POOL_WEIGHTS.values()), k=count
    )
    new_seed = random.randrange(sys.maxsize)
    return result, new_seed
