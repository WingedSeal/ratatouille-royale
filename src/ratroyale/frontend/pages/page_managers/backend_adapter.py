from typing import Callable

from ratroyale.backend.game_manager import GameManager
from ratroyale.backend.entities.rodent import Rodent
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.utils import EventQueue
from ratroyale.event_tokens.payloads import (
    SqueakPlacementPayload,
    SqueakPayload,
    GameSetupPayload,
    PlayableTiles,
    CrumbUpdatePayload,
    EntityPayload,
    AbilityActivationPayload,
    EntityMovementPayload,
    SkillTargetingPayload,
    AbilityTargetPayload,
    EntityDamagedPayload,
)
from ratroyale.backend.game_event import (
    GameEvent,
    EntitySpawnEvent,
    SqueakDrawnEvent,
    EntityMoveEvent,
    EntityDieEvent,
    FeatureDieEvent,
    EntityDamagedEvent,
    EntityHealedEvent,
    FeatureDamagedEvent,
    EntityEffectUpdateEvent,
    GameOverEvent,
    EndTurnEvent,
    SqueakPlacedEvent,
    SqueakSetResetEvent,
)
from ratroyale.backend.ai.base_ai import BaseAI
from ratroyale.backend.ai.random_ai import RandomAI
from ratroyale.backend.side import Side
from ratroyale.backend.entity import SkillTargeting, SkillCompleted


# TODO: Expand this to handle more backend events as needed. Maybe add decorator-based registration?
class BackendAdapter:
    def __init__(
        self, game_manager: GameManager, coordination_manager: CoordinationManager
    ) -> None:
        self.game_manager = game_manager
        self.coordination_manager = coordination_manager
        self.ai: BaseAI = RandomAI(self.game_manager, Side.MOUSE)
        self._ai_turn: bool = False
        self.game_manager_response: dict[str, Callable[[GameManagerEvent], None]] = {
            "start_game": self.handle_game_start,
            "squeak_tile_interaction": self.handle_squeak_tile_interaction,
            "get_squeak_placable_tiles": self.handle_squeak_placable_tiles,
            "ability_activation": self.handle_ability_activation,
            "resolve_movement": self.handle_resolve_movement,
            "end_turn": self.handle_end_turn,
            "target_selected": self.handle_target_selected,
        }
        self.game_manager_issued_events: dict[
            type[GameEvent], Callable[[GameEvent], None]
        ] = {
            EntitySpawnEvent: self.handle_spawn_entity_event,
            SqueakDrawnEvent: self.handle_squeak_drawn_event,
            EntityMoveEvent: self.handle_entity_move_event,
            EndTurnEvent: self.handle_end_turn_event,
            SqueakPlacedEvent: self.handle_squeak_placed_event,
            SqueakSetResetEvent: self.handle_squeak_set_reset_event,
            EntityDieEvent: self.handle_entity_die_event,
            FeatureDieEvent: self.handle_feature_die_event,
            EntityDamagedEvent: self.handle_entity_damaged_event,
            EntityHealedEvent: self.handle_entity_healed_event,
            FeatureDamagedEvent: self.handle_feature_damaged_event,
            EntityEffectUpdateEvent: self.handle_entity_effect_update_event,
            GameOverEvent: self.handle_game_over_event,
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
                print(msg_from_page.game_action)
                page_handler = self.game_manager_response.get(msg_from_page.game_action)
                if page_handler:
                    page_handler(msg_from_page)
                else:
                    print(
                        f"No handler for page event type: {msg_from_page.game_action}"
                    )

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
        first_side = self.game_manager.first_turn
        player_info = self.game_manager.players_info[first_side]
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

    def handle_squeak_placable_tiles(self, event: GameManagerEvent) -> None:
        payload = event.payload
        assert isinstance(payload, SqueakPayload)
        squeak = payload.squeak

        # Get placable tiles when the user clicks or drags a squeak card
        placable_tiles = squeak.get_placable_tiles(self.game_manager)
        if placable_tiles:
            self.coordination_manager.put_message(
                PageCallbackEvent(
                    callback_action="handle_squeak_placable_tiles",
                    payload=PlayableTiles(placable_tiles),
                )
            )

    def handle_ability_activation(self, event: GameManagerEvent) -> None:
        payload = event.payload
        assert isinstance(payload, AbilityActivationPayload)
        entity = payload.entity
        ability_index = payload.ability_index

        assert isinstance(entity, Rodent)

        print(ability_index)

        # -1 for movement
        if ability_index == -1:
            coord_set = self.game_manager.board.get_reachable_coords(entity)
            self.coordination_manager.put_message(
                PageCallbackEvent(
                    callback_action="reachable_coords",
                    payload=PlayableTiles(list(coord_set)),
                )
            )
        else:
            skill_result = self.game_manager.activate_skill(entity, ability_index)
            # send back results and change game board state to selection & block irrelevant functions
            if isinstance(skill_result, SkillCompleted):
                if skill_result == SkillCompleted.CANCELLED:
                    print("Skill canceled.")
                elif skill_result == SkillCompleted.SUCCESS:
                    print("Skill success.")
            elif isinstance(skill_result, SkillTargeting):
                self.coordination_manager.put_message(
                    PageCallbackEvent(
                        "skill_targeting", payload=SkillTargetingPayload(skill_result)
                    )
                )

    def handle_resolve_movement(self, event: GameManagerEvent) -> None:
        payload = event.payload
        assert isinstance(payload, EntityMovementPayload)
        entity = payload.entity
        coord = payload.path[0]

        assert isinstance(entity, Rodent)

        self.game_manager.move_rodent(entity, coord)

        self.coordination_manager.put_message(
            PageCallbackEvent(
                callback_action="crumb_update",
                payload=CrumbUpdatePayload(self.game_manager.crumbs),
            )
        )

    def handle_end_turn(self, event: GameManagerEvent) -> None:
        self.game_manager.end_turn()
        self.ai.run_ai_and_update_game_manager()

    def handle_target_selected(self, event: GameManagerEvent) -> None:
        payload = event.payload
        assert isinstance(payload, AbilityTargetPayload)
        selected_coords = payload.selected_targets
        result = self.game_manager.apply_skill_callback(selected_coords)
        print(result)

    # region Backend-produced messages

    def handle_entity_move_event(self, event: GameEvent) -> None:
        assert isinstance(event, EntityMoveEvent)
        entity = event.entity
        path = event.path
        self.coordination_manager.put_message(
            PageCallbackEvent(
                callback_action="move_entity",
                payload=EntityMovementPayload(entity, path),
            )
        )

    def handle_spawn_entity_event(self, event: GameEvent) -> None:
        assert isinstance(event, EntitySpawnEvent)
        print("spawning entity")
        entity = event.entity
        self.coordination_manager.put_message(
            PageCallbackEvent(
                callback_action="spawn_entity",
                payload=EntityPayload(entity),
            )
        )

    def handle_squeak_drawn_event(self, event: GameEvent) -> None:
        assert isinstance(event, SqueakDrawnEvent)
        hand_index = event.hand_index
        squeak = event.squeak
        if not self.ai.is_ai_turn():
            self.coordination_manager.put_message(
                PageCallbackEvent(
                    callback_action="squeak_drawn",
                    payload=SqueakPayload(hand_index, squeak),
                )
            )

    def handle_end_turn_event(self, event: GameEvent) -> None:
        assert isinstance(event, EndTurnEvent)
        print(event.__str__())
        self.coordination_manager.put_message(
            PageCallbackEvent(callback_action="end_turn")
        )
        self.coordination_manager.put_message(
            PageCallbackEvent(
                callback_action="crumb_update",
                payload=CrumbUpdatePayload(self.game_manager.crumbs),
            )
        )

    def handle_squeak_placed_event(self, event: GameEvent) -> None:
        assert isinstance(event, SqueakPlacedEvent)
        print(event.__str__())

    def handle_squeak_set_reset_event(self, event: GameEvent) -> None:
        assert isinstance(event, SqueakSetResetEvent)
        print(event.__str__())

    def handle_entity_die_event(self, event: GameEvent) -> None:
        assert isinstance(event, EntityDieEvent)
        print(event.__str__())

    def handle_feature_die_event(self, event: GameEvent) -> None:
        assert isinstance(event, FeatureDieEvent)
        print(event.__str__())

    def handle_entity_damaged_event(self, event: GameEvent) -> None:
        assert isinstance(event, EntityDamagedEvent)
        print(event.__str__())
        CoordinationManager.put_message(
            PageCallbackEvent(
                "entity_damaged",
                payload=EntityDamagedPayload(
                    entity=event.entity,
                    damage=event.damage,
                    hp_loss=event.hp_loss,
                    source=event.source,
                ),
            )
        )

    def handle_entity_healed_event(self, event: GameEvent) -> None:
        assert isinstance(event, EntityHealedEvent)
        print(event.__str__())

    def handle_feature_damaged_event(self, event: GameEvent) -> None:
        assert isinstance(event, FeatureDamagedEvent)
        print(event.__str__())

    def handle_entity_effect_update_event(self, event: GameEvent) -> None:
        assert isinstance(event, EntityEffectUpdateEvent)
        print(event.__str__())

    def handle_game_over_event(self, event: GameEvent) -> None:
        assert isinstance(event, GameOverEvent)
        print(event.__str__())
