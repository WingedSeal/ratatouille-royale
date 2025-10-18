from typing import Any, Callable

from ratroyale.backend.board import Board
from ratroyale.backend.entity import Entity
from ratroyale.backend.game_manager import GameManager
from ratroyale.backend.hexagon import OddRCoord
from ratroyale.backend.tile import Tile
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.utils import EventQueue
from ratroyale.event_tokens.payloads import (
    SqueakPlacementPayload,
    SqueakPayload,
    GameSetupPayload,
    SqueakPlacableTilesPayload,
    CrumbUpdatePayload,
)
from ratroyale.backend.side import Side


# TODO: Expand this to handle more backend events as needed. Maybe add decorator-based registration?
class BackendAdapter:
    def __init__(
        self, game_manager: GameManager, coordination_manager: CoordinationManager
    ) -> None:
        self.game_manager = game_manager
        self.coordination_manager = coordination_manager
        self.event_to_action_map: dict[str, Callable[[GameManagerEvent[Any]], None]] = {
            "start_game": self.handle_game_start,
            "squeak_tile_interaction": self.handle_squeak_tile_interaction,
            "get_squeak_placable_tiles": self.handld_squeak_placable_tiles,
        }

    def execute_backend_callback(self) -> None:
        msg_queue: EventQueue[GameManagerEvent[Any]] | None = (
            self.coordination_manager.mailboxes.get(GameManagerEvent, None)
        )
        if not msg_queue:
            return

        while not msg_queue.empty():
            msg = msg_queue.get()
            handler = self.event_to_action_map.get(msg.game_action, None)
            if handler:
                handler(msg)
            else:
                print(f"No handler for event type {type(msg)}")

    def handle_game_start(self, event: GameManagerEvent[None]) -> None:
        board = self.game_manager.board
        # TODO: Which side is the player's side?
        player_info = self.game_manager.players_info[Side.RAT]
        squeak_in_hand_list = player_info.get_squeak_set().get_deck_and_hand()[1]
        self.coordination_manager.put_message(
            PageCallbackEvent(
                callback_action="start_game",
                payload=GameSetupPayload(
                    board=board,
                    hand_squeaks=squeak_in_hand_list,
                    starting_crumbs=self.game_manager.crumbs,
                ),
            )
        )

    def handle_squeak_tile_interaction(
        self, event: GameManagerEvent[SqueakPlacementPayload]
    ) -> None:
        payload = event.payload
        if payload:
            hand_index = payload.hand_index
            coord = payload.tile_coord

            # Validate crumb on frontend by disabling unplayable cards.
            self.game_manager.place_squeak(hand_index, coord)
            self.coordination_manager.put_message(
                PageCallbackEvent(
                    callback_action="crumb_update",
                    payload=CrumbUpdatePayload(self.game_manager.crumbs),
                )
            )

    def handld_squeak_placable_tiles(
        self, event: GameManagerEvent[SqueakPayload]
    ) -> None:
        payload = event.payload
        assert payload
        squeak = payload.squeak

        # Get placable tiles when the user clicks or drags a squeak card
        placable_tiles = squeak.get_placable_tiles(self.game_manager)
        print("Placable tiles for selected squeak:")
        for coord in placable_tiles:
            print(f"Placable tile at {coord}")
        if placable_tiles:
            self.coordination_manager.put_message(
                PageCallbackEvent(
                    callback_action="handle_squeak_placable_tiles",
                    payload=SqueakPlacableTilesPayload(placable_tiles),
                )
            )


def get_name_from_entity(entity: Entity) -> str:
    """Translate an Entity instance to a representative string name"""
    return f"entity_{entity.name}_{entity.pos.x}_{entity.pos.y}"


def get_name_from_tile(tile: Tile) -> str:
    """Translate a Tile instance to a representative string name"""
    return f"tile_{tile.coord.x}_{tile.coord.y}"


def get_entity_from_name(board: Board, name: str) -> Entity | None:
    """Translate a string name to an Entity instance. \n
    Format: entity_{entity.name}_{entity.pos.x}_{entity.pos.y}"""
    name_parts = name.split("_")
    entity_name = name_parts[1]
    pos_x = int(name_parts[-2])
    pos_y = int(name_parts[-1])
    coord = OddRCoord(pos_x, pos_y)

    tile = board.get_tile(coord)
    if tile is not None:
        entities_here = tile.entities
        for entity in entities_here:
            if entity.name == entity_name and entity.pos == coord:
                return entity
            else:
                raise ValueError(f"Entity with name {name} not found on board.")

    return None


def get_tile_from_name(board: Board, name: str) -> Tile:
    """Translate a string name to an Tile instance. \n
    Format: tile_{tile.coord.x}_{tile.coord.y}"""
    name_parts = name.split("_")
    pos_x = int(name_parts[-2])
    pos_y = int(name_parts[-1])
    coord = OddRCoord(pos_x, pos_y)

    tile = board.get_tile(coord)

    if tile:
        return tile
    else:
        raise ValueError(f"No tile found at {coord}")
