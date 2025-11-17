from dataclasses import dataclass
from ratroyale.backend.map import Map
from ratroyale.backend.player_info.player_info import PlayerInfo
from ratroyale.backend.tile import Tile
from ratroyale.backend.entity import Entity
from ratroyale.backend.hexagon import OddRCoord
from ratroyale.backend.board import Board
from ratroyale.backend.player_info.squeak import Squeak
from ratroyale.backend.entity import SkillTargeting, SkillCompleted
from ratroyale.backend.instant_kill import InstantKill
from ratroyale.backend.source_of_damage_or_heal import SourceOfDamageOrHeal
from ratroyale.backend.ai.base_ai import BaseAI
from ratroyale.backend.side import Side
from ratroyale.backend.crumbs_per_turn_modifier import CrumbsPerTurnModifier
from pathlib import Path


@dataclass
class Payload:
    pass


@dataclass
class BackendStartPayload(Payload):
    map: Map
    player_info1: PlayerInfo
    player_info2: PlayerInfo
    player_1: Side
    ai_type: type[BaseAI] | None


@dataclass
class EntityDamagedPayload(Payload):
    entity: Entity
    damage: int | InstantKill
    hp_loss: int
    source: SourceOfDamageOrHeal


@dataclass
class TilePayload(Payload):
    tile: Tile


@dataclass
class IntegerPayload(Payload):
    value: int


@dataclass
class GameSetupPayload(Payload):
    crumbs_modifier: CrumbsPerTurnModifier
    board: Board
    player1_squeaks: list[Squeak]
    player2_squeaks: list[Squeak]
    starting_crumbs: int
    player_1_side: Side
    playing_with_ai: bool


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
class SkillActivationPayload(Payload):
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
class PlayableTilesPayload(Payload):
    coord_list: list[OddRCoord]


@dataclass
class SqueakPlacementPayload(Payload):
    hand_index: int
    tile_coord: OddRCoord


@dataclass
class EntityMovementPayload(Payload):
    entity: Entity
    coord_list: list[OddRCoord]


@dataclass
class SkillTargetingPayload(Payload):
    skill_targeting: SkillTargeting | SkillCompleted


@dataclass
class GameOverPayload(Payload):
    is_winner_from_player_1_side: bool
    victory_side: Side


@dataclass
class MoveHistoryPayload(Payload):
    entity_name: str
    from_pos: OddRCoord
    to_pos: OddRCoord
    turn: int
    side: Side


@dataclass
class FeaturePayload(Payload):
    feature_name: str
    feature_description: str
    feature_type: str


@dataclass
class TurnPayload(Payload):
    turn_number: int
    current_turn_number: int
    current_side: Side
    crumbs_modifier: CrumbsPerTurnModifier
    jump_to_turn: int | None = None


@dataclass
class SidePayload(Payload):
    side: Side


@dataclass
class DeckPayload(Payload):
    deck: list[Squeak]


@dataclass
class SaveFilesPayload(Payload):
    save_files: list[str]


@dataclass
class PlayerInfoPayload(Payload):
    player_info: PlayerInfo
    path: Path | None
