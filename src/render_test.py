# ruff: noqa

import pygame

from ratroyale.backend.entities.rodents.vanguard import TailBlazer
from ratroyale.backend.entity import Entity
from ratroyale.backend.game_manager import GameManager
from ratroyale.backend.hexagon import OddRCoord
from ratroyale.backend.player_info.player_info import PlayerInfo
from ratroyale.backend.player_info.squeak import (
    Squeak,
    SqueakGetPlacableTiles,
    SqueakOnPlace,
    SqueakType,
    rodent_placable_tile,
    summon_on_place,
)
from ratroyale.backend.features.common import DeploymentZone
from ratroyale.backend.side import Side
from ratroyale.backend.tile import Tile
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.page_token import PageNavigation, PageNavigationEvent
from ratroyale.frontend.pages.page_managers.backend_adapter import BackendAdapter
from ratroyale.frontend.pages.page_managers.page_manager import PageManager
from ratroyale.frontend.visual.screen_constants import SCREEN_SIZE

from ratroyale.backend.features.common import Lair
from ratroyale.backend.map import Map, heights_to_tiles
from ratroyale.backend.side import Side

import random


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    clock = pygame.time.Clock()

    coordination_manager = CoordinationManager()

    page_manager = PageManager(screen=screen, coordination_manager=coordination_manager)

    # region GAME MANAGER DOMAIN
    entities: list[Entity] = [TailBlazer(OddRCoord(1, 3))]
    mouse_zone = DeploymentZone(
        shape=[OddRCoord(0, 1), OddRCoord(1, 0)], side=Side.MOUSE
    )
    rat_zone = DeploymentZone(shape=[OddRCoord(5, 5), OddRCoord(5, 4)], side=Side.RAT)
    map = Map(
        "Example Map",
        6,
        6,
        heights_to_tiles(
            [
                [1, 1, 1, 1, 1, None],
                [1, 2, 2, 1, 1, 1],
                [1, 2, 2, 3, 1, 1],
                [1, 1, 3, 3, 1, 1],
                [1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1],
            ]
        ),
        entities=entities,
        features=[Lair([OddRCoord(0, 0)], 10, side=Side.RAT), mouse_zone, rat_zone],
    )

    # Create dummy squeaks that interact with the game manager
    dummy_squeaks = [
        Squeak(
            name=f"Test Card {i}",
            crumb_cost=random.randint(1, 6) * 10,
            squeak_type=SqueakType.RODENT,
            on_place=summon_on_place(TailBlazer),  # uses actual summon_on_place
            get_placable_tiles=rodent_placable_tile,  # uses actual placement logic
            rodent=TailBlazer,
        )
        for i in range(10)
    ]

    # Indices for deck and hand
    all_indices = set(range(5))

    # Player 1: create a SqueakSet directly in the constructor
    player_info_1 = PlayerInfo(
        all_squeaks=dummy_squeaks.copy(),
        squeak_sets=[set(range(10))],  # deck indices for SqueakSet
        hands=[all_indices],  # hand indices for SqueakSet
        selected_squeak_set_index=0,
    )

    # Player 2: separate SqueakSet instance
    player_info_2 = PlayerInfo(
        all_squeaks=dummy_squeaks.copy(),
        squeak_sets=[set(range(10))],
        hands=[all_indices],
        selected_squeak_set_index=0,
    )

    game_manager = GameManager(
        map=map, players_info=(player_info_1, player_info_2), first_turn=Side.RAT
    )
    # endregion

    backend_adapter = BackendAdapter(
        game_manager=game_manager, coordination_manager=coordination_manager
    )

    coordination_manager.put_message(
        PageNavigationEvent(
            action_list=[(PageNavigation.OPEN, "GameBoard")]
        )  # change this to test your page
    )

    while coordination_manager.game_running:
        dt = clock.tick(60) / 1000.0  # delta time in seconds

        screen.fill((0, 0, 0))
        page_manager.handle_events()

        while not coordination_manager.all_mailboxes_empty():
            page_manager.execute_page_callback()
            page_manager.execute_visual_callback()
            backend_adapter.execute_backend_callback()

        page_manager.render(dt)

        pygame.display.flip()

    # Cleanup process
    pygame.quit()


if __name__ == "__main__":
    main()
