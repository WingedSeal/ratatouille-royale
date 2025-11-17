from typing import TYPE_CHECKING, Callable

from ratroyale.backend.game_manager import GameManager
from ratroyale.backend.entities.rodent import Rodent
from ratroyale.backend.game_event import *
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.utils import EventQueue
from ratroyale.event_tokens.payloads import (
    SqueakPlacementPayload,
    SqueakPayload,
    GameSetupPayload,
    PlayableTilesPayload,
    CrumbUpdatePayload,
    SkillActivationPayload,
    EntityMovementPayload,
    SkillTargetingPayload,
    AbilityTargetPayload,
    EntityDamagedPayload,
    EntityPayload,
    GameOverPayload,
    SidePayload,
    DeckPayload,
)
from ratroyale.backend.game_event import (
    GameEvent,
)
from ratroyale.backend.ai.base_ai import BaseAI
from ratroyale.backend.side import Side

if TYPE_CHECKING:
    from ratroyale.frontend.pages.page_managers.page_manager import PageManager


# TODO: Expand this to handle more backend events as needed. Maybe add decorator-based registration?
class BackendAdapter:
    def __init__(
        self,
        game_manager: GameManager,
        page_manager: "PageManager",
        coordination_manager: CoordinationManager,
        ai_type: type[BaseAI] | None,
    ) -> None:
        self.game_manager = game_manager
        self.page_manager = page_manager
        self.coordination_manager = coordination_manager
        self.ai: BaseAI | None = (
            ai_type(self.game_manager, Side.MOUSE) if ai_type else None
        )
        self._ai_turn: bool = False
        self.game_manager_response: dict[str, Callable[[GameManagerEvent], None]] = {
            "start_game": self.handle_game_start,
            "squeak_tile_interaction": self.handle_squeak_tile_interaction,
            "get_squeak_placable_tiles": self.handle_squeak_placable_tiles,
            "ability_activation": self.handle_ability_activation,
            "resolve_movement": self.handle_resolve_movement,
            "end_turn": self.handle_end_turn,
            "target_selected": self.handle_target_selected,
            "skill_canceled": self.handle_skill_canceled,
            "inspect_deck_clicked": self.handle_inspect_deck_clicked,
            "get_player_1": self.handle_get_player_1,
        }

    def execute_backend_callback(self) -> None:
        msg_queue_from_backend: EventQueue[GameEvent] = self.game_manager.event_queue

        # Process all messages currently in both queues
        while not msg_queue_from_backend.empty():
            msg_from_backend: GameEvent = msg_queue_from_backend.get()

            self.page_manager.execute_game_event_callback(msg_from_backend)

    def handle_game_start(self, event: GameManagerEvent) -> None:
        board = self.game_manager.board

        player_1_side = self.game_manager.player_1
        squeak_in_player_1_hand_list = self.game_manager.hands[player_1_side]
        squeak_in_player_2_hand_list = self.game_manager.hands[
            player_1_side.other_side()
        ]

        self.coordination_manager.put_message(
            PageCallbackEvent(
                callback_action="start_game",
                payload=GameSetupPayload(
                    crumbs_modifier=self.game_manager.crumbs_per_turn_modifier,
                    board=board,
                    player1_squeaks=squeak_in_player_1_hand_list,
                    player2_squeaks=squeak_in_player_2_hand_list,
                    starting_crumbs=self.game_manager.crumbs,
                    player_1_side=player_1_side,
                    playing_with_ai=self.ai is not None,
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

    def handle_skill_canceled(self, event: GameManagerEvent) -> None:
        self.game_manager.cancel_selecting_target()

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
                    payload=PlayableTilesPayload(list(placable_tiles)),
                )
            )

    def handle_ability_activation(self, event: GameManagerEvent) -> None:
        payload = event.payload
        assert isinstance(payload, SkillActivationPayload)
        entity = payload.entity
        ability_index = payload.ability_index

        assert isinstance(entity, Rodent)

        # -1 is for for movement
        if ability_index == -1:
            coord_set = self.game_manager.board.get_reachable_coords(entity)
            self.coordination_manager.put_message(
                PageCallbackEvent(
                    callback_action="reachable_coords",
                    payload=EntityMovementPayload(entity, list(coord_set)),
                )
            )
        else:
            skill_result = self.game_manager.activate_skill(entity, ability_index)
            # send back results and change game board state to selection & block irrelevant functions
            self.coordination_manager.put_message(
                PageCallbackEvent(
                    "skill_targeting",
                    payload=SkillTargetingPayload(skill_result),
                )
            )
            self.coordination_manager.put_message(
                PageCallbackEvent(
                    "crumb_update",
                    payload=CrumbUpdatePayload(self.game_manager.crumbs),
                )
            )

    def handle_resolve_movement(self, event: GameManagerEvent) -> None:
        payload = event.payload
        assert isinstance(payload, EntityMovementPayload)
        entity = payload.entity
        coord = payload.coord_list[0]

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
        if self.ai:
            self.ai.run_ai_and_update_game_manager()

    def handle_target_selected(self, event: GameManagerEvent) -> None:
        payload = event.payload
        assert isinstance(payload, AbilityTargetPayload)
        selected_coords = payload.selected_targets
        skill_result = self.game_manager.apply_skill_callback(selected_coords)
        CoordinationManager.put_message(
            PageCallbackEvent(
                "skill_targeting",
                payload=SkillTargetingPayload(skill_result),
            )
        )

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
        CoordinationManager.put_message(
            PageCallbackEvent("entity_died", payload=EntityPayload(event.entity))
        )

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
        CoordinationManager.put_message(
            PageCallbackEvent(
                "game_over",
                payload=GameOverPayload(
                    event.is_winner_from_player_1_side, event.victory_side
                ),
            )
        )

    def handle_inspect_deck_clicked(self, event: GameManagerEvent) -> None:
        payload = event.payload
        assert isinstance(payload, SidePayload)
        side = payload.side
        deck = self.game_manager.decks[side]
        self.coordination_manager.put_message(
            PageCallbackEvent(
                callback_action="inspect_deck",
                payload=DeckPayload(deck=deck),
            )
        )

    def handle_get_player_1(self, event: GameManagerEvent) -> None:
        player_1_side = self.game_manager.player_1
        self.coordination_manager.put_message(
            PageCallbackEvent(
                callback_action="player_1_info",
                payload=SidePayload(side=player_1_side),
            )
        )
