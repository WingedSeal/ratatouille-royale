from typing import Callable

from ratroyale.backend.game_manager import GameManager
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
    EntityPayload,
)
from ratroyale.backend.side import Side
from ratroyale.backend.game_event import GameEvent, EntitySpawnEvent


# TODO: Expand this to handle more backend events as needed. Maybe add decorator-based registration?
class BackendAdapter:
    def __init__(
        self, game_manager: GameManager, coordination_manager: CoordinationManager
    ) -> None:
        self.game_manager = game_manager
        self.coordination_manager = coordination_manager
        self.game_manager_response: dict[str, Callable[[GameManagerEvent], None]] = {
            "start_game": self.handle_game_start,
            "squeak_tile_interaction": self.handle_squeak_tile_interaction,
            "get_squeak_placable_tiles": self.handld_squeak_placable_tiles,
        }
        self.game_manager_issued_events: dict[
            type[GameEvent], Callable[[GameEvent], None]
        ] = {
            EntitySpawnEvent: self.spawn_entity_event_handler,
        }

    def execute_backend_callback(self) -> None:
        # Get the page -> backend queue
        msg_queue_from_page: EventQueue[GameManagerEvent] | None = (
            self.coordination_manager.mailboxes.get(GameManagerEvent, None)
        )
        # Get the backend -> page queue
        msg_queue_from_backend: EventQueue[GameEvent] = self.game_manager.event_queue

        if msg_queue_from_page is None:
            return

        # Process all messages currently in both queues
        while not msg_queue_from_page.empty() or not msg_queue_from_backend.empty():
            # Process page -> backend messages
            if not msg_queue_from_page.empty():
                msg_from_page: GameManagerEvent = msg_queue_from_page.get()
                page_handler = self.game_manager_response.get(msg_from_page.game_action)
                if page_handler:
                    page_handler(msg_from_page)
                else:
                    print(f"No handler for page event type: {type(msg)}")

            # Process backend -> page messages
            if not msg_queue_from_backend.empty():
                msg: GameEvent = msg_queue_from_backend.get()
                handler = self.game_manager_issued_events.get(type(msg))
                if handler:
                    handler(msg)
                else:
                    print(f"No handler for backend event type: {type(msg)}")

    def handle_game_start(self, event: GameManagerEvent) -> None:
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

    def handle_squeak_tile_interaction(self, event: GameManagerEvent) -> None:
        payload = event.payload
        if payload:
            assert isinstance(payload, SqueakPlacementPayload)
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

    def handld_squeak_placable_tiles(self, event: GameManagerEvent) -> None:
        payload = event.payload
        assert isinstance(payload, SqueakPayload)
        squeak = payload.squeak

        # Get placable tiles when the user clicks or drags a squeak card
        placable_tiles = squeak.get_placable_tiles(self.game_manager)
        if placable_tiles:
            self.coordination_manager.put_message(
                PageCallbackEvent(
                    callback_action="handle_squeak_placable_tiles",
                    payload=SqueakPlacableTilesPayload(placable_tiles),
                )
            )

    def spawn_entity_event_handler(self, event: GameEvent) -> None:
        assert isinstance(event, EntitySpawnEvent)
        entity = event.entity
        self.coordination_manager.put_message(
            PageCallbackEvent(
                callback_action="spawn_entity",
                payload=EntityPayload(entity),
            )
        )
