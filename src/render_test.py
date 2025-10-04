# type: ignore
import pygame
from ratroyale.frontend.pages.page_managers.page_manager import PageManager
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.frontend.visual.screen_constants import SCREEN_SIZE
import ratroyale.frontend.pages.page_definitions as pages

from ratroyale.backend.game_manager import GameManager
from ratroyale.backend.map import Map
from ratroyale.backend.player_info.player_info import PlayerInfo
from ratroyale.backend.tile import Tile
from ratroyale.backend.hexagon import OddRCoord
from ratroyale.backend.entities.rodents.vanguard import TailBlazer
from ratroyale.backend.entity import Entity
from ratroyale.backend.side import Side
from ratroyale.backend.player_info.squeak import (
    Squeak,
    SqueakType,
    SqueakOnPlace,
    SqueakGetPlacableTiles,
)

def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    clock = pygame.time.Clock()

    coordination_manager = CoordinationManager()

    page_manager = PageManager(screen=screen, coordination_manager=coordination_manager)

    # region GAME MANAGER DOMAIN
    size_x, size_y = 5, 10
    tiles: list[list[Tile | None]] = []
    for q in range(size_x):
        row = []
        for r in range(size_y):
            tile = Tile(coord=OddRCoord(q, r), entities=[], height=0, features=[])
            row.append(tile)
        tiles.append(row)
    entities: list[Entity] = [TailBlazer(OddRCoord(1, 3))]

    # Dummy callables
    dummy_on_place: SqueakOnPlace = lambda game_manager, coord: None
    dummy_get_placable: SqueakGetPlacableTiles = lambda game_manager: []

    # Create 5 dummy squeaks
    dummy_squeaks = [
        Squeak(
            crumb_cost=1,
            squeak_type=SqueakType.RODENT,
            on_place=dummy_on_place,
            get_placable_tiles=dummy_get_placable,
        )
        for i in range(5)
    ]

    # Example squeak sets (just indices into dummy_squeaks)
    dummy_squeak_sets = [set(range(len(dummy_squeaks)))]
    selected_index = 0

    # PlayerInfo
    player_info_1 = PlayerInfo(
        all_squeaks=dummy_squeaks,
        squeak_sets=dummy_squeak_sets,
        selected_squeak_set_index=selected_index,
    )

    player_info_2 = PlayerInfo(
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
        features=[],
    )
    game_manager = GameManager(
        map=map,
        players_info=(player_info_1, player_info_2),
        first_turn=Side.MOUSE,
        coordination_manager=coordination_manager,
    )
    # endregion

    page_manager.push_page(pages.MainMenu)

    while coordination_manager.game_running:
        dt = clock.tick(60) / 1000.0  # delta time in seconds

        screen.fill((0, 0, 0))
        page_manager.handle_events()

        while not coordination_manager.all_mailboxes_empty():
            page_manager.execute_page_callback()
            page_manager.execute_visual_callback()

        page_manager.render(dt)

        pygame.display.flip()

    # Cleanup process
    pygame.quit()


if __name__ == "__main__":
    main()
