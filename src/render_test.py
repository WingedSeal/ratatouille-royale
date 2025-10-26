# ruff: noqa

import pygame

pygame.init()

from ratroyale.backend.ai.rushb_ai import RushBAI
from ratroyale.backend.player_info.squeaks.rodents.vanguard import TAIL_BLAZER
from ratroyale.backend.player_info.squeaks.rodents.duelist import (
    RATBERT_BREWBELLY,
    SODA_KABOOMA,
    MORTAR,
)
from ratroyale.backend.player_info.squeaks.rodents.specialist import MAYO
from ratroyale.backend.player_info.squeaks.rodents.tank import CRACKER
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
from ratroyale.backend.ai.random_ai import RandomAI

from ratroyale.backend.features.common import Lair, DeploymentZone
from ratroyale.backend.map import Map, heights_to_tiles
from ratroyale.backend.side import Side
from ratroyale.backend.hexagon import OddRCoord
import cProfile
import pstats

import random


def main():
    screen = pygame.display.set_mode(SCREEN_SIZE)
    clock = pygame.time.Clock()

    coord = OddRCoord(15, 15)
    to_pixel = coord.to_pixel(64, 64, is_bounding_box=True)
    print("TO PIXEL:", to_pixel)
    from_pixel = OddRCoord.from_pixel(*to_pixel, 64, is_bounding_box=True)
    print("FROM PIXEL:", from_pixel)

    coordination_manager = CoordinationManager()

    page_manager = PageManager(screen=screen, coordination_manager=coordination_manager)

    # region GAME MANAGER DOMAIN
    mouse_zone = DeploymentZone(
        shape=[OddRCoord(0, 1), OddRCoord(1, 0)], side=Side.MOUSE
    )
    rat_zone = DeploymentZone(shape=[OddRCoord(4, 5), OddRCoord(5, 4)], side=Side.RAT)
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
        entities=[],
        features=[
            Lair([OddRCoord(0, 0)], 10, side=Side.MOUSE),
            Lair([OddRCoord(5, 5)], 10, side=Side.RAT),
            mouse_zone,
            rat_zone,
        ],
    )
    size = 10
    map = Map(
        "Example Map",
        size,
        size,
        heights_to_tiles([[1 for i in range(size)] for i in range(size)]),
        entities=[],
        features=[
            Lair([OddRCoord(0, 0)], 10, side=Side.MOUSE),
            Lair([OddRCoord(size - 1, size - 1)], 10, side=Side.RAT),
            DeploymentZone(shape=[OddRCoord(0, 1), OddRCoord(1, 0)], side=Side.MOUSE),
            DeploymentZone(
                shape=[OddRCoord(size - 2, size - 1), OddRCoord(size - 1, size - 2)],
                side=Side.RAT,
            ),
        ],
    )

    # Player 1: create a SqueakSet directly in the constructor
    player_info_1 = PlayerInfo(
        {TAIL_BLAZER: 5},
        [{TAIL_BLAZER: 5}],
        [{TAIL_BLAZER: 5}],
        selected_squeak_set_index=0,
        exp=0,
        cheese=0,
        is_progression_frozen=True,
    )

    # Player 2: separate SqueakSet instance
    player_info_2 = PlayerInfo(
        {TAIL_BLAZER: 5},
        [{TAIL_BLAZER: 5}],
        [{TAIL_BLAZER: 5}],
        selected_squeak_set_index=0,
        exp=0,
        cheese=0,
        is_progression_frozen=True,
    )

    game_manager = GameManager(
        map=map, players_info=(player_info_1, player_info_2), first_turn=Side.RAT
    )
    # endregion

    backend_adapter = BackendAdapter(
        game_manager=game_manager,
        page_manager=page_manager,
        coordination_manager=coordination_manager,
        ai_type=RandomAI,
    )

    coordination_manager.put_message(
        PageNavigationEvent(
            action_list=[
                (PageNavigation.OPEN, "InspectFeature"),
            ]
        )  # change this to test your page
    )

    avg_fps = 0
    fps_alpha = 0.1  # smoothing factor for running average

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

        # Compute current FPS
        current_fps = clock.get_fps()
        if current_fps > 0:  # avoid initial division by zero
            avg_fps = (1 - fps_alpha) * avg_fps + fps_alpha * current_fps

    # Cleanup process
    pygame.quit()
    # print(f"Avg FPS: {avg_fps:.2f}")


if __name__ == "__main__":
    # profiler = cProfile.Profile()
    # profiler.enable()
    main()
    # profiler.disable()

    # stats = pstats.Stats(profiler)
    # stats.strip_dirs().sort_stats("tottime").print_stats(20)
