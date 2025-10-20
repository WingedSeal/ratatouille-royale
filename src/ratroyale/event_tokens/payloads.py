from dataclasses import dataclass
from ratroyale.backend.tile import Tile
from ratroyale.backend.entity import Entity
from ratroyale.backend.hexagon import OddRCoord
from ratroyale.backend.board import Board
from ratroyale.backend.player_info.squeak import Squeak
from typing import Iterable
from ratroyale.backend.entity import SkillTargeting
from ratroyale.backend.instant_kill import InstantKill
from ratroyale.backend.source_of_damage_or_heal import SourceOfDamageOrHeal
from ratroyale.backend.side import Side


@dataclass
class Payload:
    pass


@dataclass
class EntityDamagedPayload(Payload):
    entity: Entity
    damage: int | InstantKill
    hp_loss: int
    source: SourceOfDamageOrHeal
    pass


@dataclass
class TilePayload(Payload):
    tile: Tile


@dataclass
class GameSetupPayload(Payload):
    board: Board
    hand_squeaks: list[Squeak]
    starting_crumbs: int
    player_1_side: Side


@dataclass
class CrumbUpdatePayload(Payload):
    new_crumb_amount: int


@dataclass
class SqueakDrawnPayload(Payload):
    squeak: Squeak


@dataclass
class EntityPayload(Payload):
    entity: Entity


@dataclass
class AbilityActivationPayload(Payload):
    ability_index: int
    entity: Entity


@dataclass
class AbilityTargetPayload(Payload):
    selected_targets: list[OddRCoord]


@dataclass
class SqueakPayload(Payload):
    hand_index: int
    squeak: Squeak


@dataclass
class PlayableTiles(Payload):
    coord_list: Iterable[OddRCoord]


@dataclass
class SqueakPlacementPayload(Payload):
    hand_index: int
    tile_coord: OddRCoord


@dataclass
class EntityMovementPayload(Payload):
    entity: Entity
    path: list[OddRCoord]


@dataclass
class SkillTargetingPayload(Payload):
    skill_targeting: SkillTargeting
