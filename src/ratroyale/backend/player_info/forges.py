from .squeaks.rodents.tank import CRACKER
from .squeaks.rodents.vanguard import TAILBLAZER, TAILTRAIL
from .squeak import Squeak


FORGES: list[tuple[dict[Squeak, int], Squeak]] = [
    ({TAILBLAZER: 10, CRACKER: 1}, TAILTRAIL)
]
