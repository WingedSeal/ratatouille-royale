from typing import Iterable
from .entities.rodent import Rodent
from .entity import CallableEntitySkill
from .hexagon import OddRCoord
from .board import Board

def get_attackable_coords(
    board: Board, rodent: Rodent, skill: CallableEntitySkill
) -> Iterable[OddRCoord]: ...
