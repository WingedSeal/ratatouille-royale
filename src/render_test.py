# ruff: noqa
# type: ignore
import pygame

from ratroyale.backend.entities.rodents.vanguard import TailBlazer
from ratroyale.backend.entity import Entity
from ratroyale.backend.game_manager import GameManager
from ratroyale.backend.hexagon import OddRCoord
from ratroyale.backend.map import Map
from ratroyale.backend.player_info.player_info import PlayerInfo
from ratroyale.backend.player_info.squeak import (
    Squeak,
    SqueakGetPlacableTiles,
    SqueakOnPlace,
    SqueakType,
)
from ratroyale.backend.side import Side
from ratroyale.backend.tile import Tile
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.page_token import PageNavigation, PageNavigationEvent
from ratroyale.frontend.pages.page_managers.backend_adapter import BackendAdapter
from ratroyale.frontend.pages.page_managers.page_manager import PageManager
from ratroyale.frontend.visual.screen_constants import SCREEN_SIZE
from ratroyale.backend.features.common import Lair, DeploymentZone


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    clock = pygame.time.Clock()

    coordination_manager = CoordinationManager()

    page_manager = PageManager(screen=screen, coordination_manager=coordination_manager)

    # region GAME MANAGER DOMAIN
    size_x, size_y = 5, 10
    tiles: list[list[Tile | None]] = []
    for q in range(size_y):
        row = []
        for r in range(size_x):
            tile = Tile(
                tile_id=1, coord=OddRCoord(r, q), entities=[], height=0, features=[]
            )
            row.append(tile)
        tiles.append(row)
    entities: list[Entity] = [TailBlazer(OddRCoord(1, 3))]

    # Dummy callables
    dummy_on_place: SqueakOnPlace = lambda game_manager, coord: None
    dummy_get_placable: SqueakGetPlacableTiles = lambda game_manager: []

    # Create 5 dummy squeaks
    dummy_squeaks = [
        Squeak(
            name="Test Card",
            crumb_cost=1,
            squeak_type=SqueakType.RODENT,
            on_place=dummy_on_place,
            get_placable_tiles=dummy_get_placable,
            rodent=TailBlazer,
        )
        for i in range(5)
    ]

    # Example squeak sets (just indices into dummy_squeaks)
    dummy_squeak_sets = [set(range(len(dummy_squeaks)))]
    selected_index = 0

    # PlayerInfo
    player_info_1 = PlayerInfo(
        hands=[[0, 1, 2, 3, 4]],
        all_squeaks=dummy_squeaks,
        squeak_sets=dummy_squeak_sets,
        selected_squeak_set_index=selected_index,
    )

    player_info_2 = PlayerInfo(
        hands=[[0, 1, 2, 3, 4]],
        all_squeaks=dummy_squeaks,
        squeak_sets=dummy_squeak_sets,
        selected_squeak_set_index=selected_index,
    )

    map = Map(
        name="",
        size_x=size_x,
        size_y=size_y,
        tiles=tiles,
        entities=entities,
        features=[
            Lair(
                shape=[
                    OddRCoord(0, 0),
                    OddRCoord(0, 1),
                    OddRCoord(1, 0),
                    OddRCoord(1, 1),
                ],
                side=Side.MOUSE,
            )
        ],
    )
    game_manager = GameManager(
        map=map, players_info=(player_info_1, player_info_2), first_turn=Side.MOUSE
    )
    # endregion

    backend_adapter = BackendAdapter(
        game_manager=game_manager, coordination_manager=coordination_manager
    )

    coordination_manager.put_message(
        PageNavigationEvent(
            action_list=[
                (PageNavigation.OPEN, "MainMenu"),
            ]
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
