from ratroyale.backend.game_manager import GameManager
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.page_token import *
from typing import Callable
from ratroyale.backend.board import Board
from ratroyale.backend.tile import Tile
from ratroyale.backend.entity import Entity, EntitySkill
from ratroyale.backend.hexagon import OddRCoord

# TODO: Expand this to handle more backend events as needed. Maybe add decorator-based registration?
class BackendAdapter:
    def __init__(self, game_manager: GameManager, coordination_manager: CoordinationManager) -> None:
        self.game_manager = game_manager
        self.coordination_manager = coordination_manager
        self.event_to_action_map: dict[str, Callable[[GameManagerEvent], None]] = {
              "start_game": self.handle_game_start,
              "entity_list": self.handle_entity_list
          }
        
    def execute_backend_callback(self) -> None:
        msg_queue = self.coordination_manager.mailboxes.get(GameManagerEvent, None)
        if not msg_queue:
            return 
        
        while not msg_queue.empty():
            msg = msg_queue.get()
            handler = self.event_to_action_map.get(msg.game_action, None)
            if handler:
                handler(msg)
            else:
                print(f"No handler for event type {type(msg)}")

    def handle_game_start(self, event: GameManagerEvent) -> None:
        board = self.game_manager.board
        if board:
            self.coordination_manager.put_message(PageCallbackEvent[Board](
                callback_action="start_game",
                payload=board
            ))
        else:
            self.coordination_manager.put_message(PageCallbackEvent(
                callback_action="start_game",
                success=False,
                error_msg="Failed to start game: Board not initialized",
                payload=None
            ))

    def handle_entity_list(self, event: GameManagerEvent) -> None:
        board = self.game_manager.board
        entity_list = board.cache.entities

        self.coordination_manager.put_message(PageCallbackEvent[list[Entity]](
            callback_action="entity_list",
            payload=entity_list
        ))


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
        