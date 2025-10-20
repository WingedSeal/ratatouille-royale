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
                tile_id=1, coord=OddRCoord(q, r), entities=[], height=0, features=[]
            )
            row.append(tile)
        tiles.append(row)
    entities: list[Entity] = [TailBlazer(OddRCoord(1, 3))]

    # Dummy callables
    dummy_on_place: SqueakOnPlace = lambda game_manager, coord: None
    dummy_get_placable: SqueakGetPlacableTiles = lambda game_manager: []

    # Create 5 dummy squeaks

    # PlayerInfo
    player_info_1 = PlayerInfo(
        {TAIL_BLAZER: 5}, [{TAIL_BLAZER: 5}], [{TAIL_BLAZER: 5}], 0
    )

    player_info_2 = PlayerInfo(
        {TAIL_BLAZER: 5}, [{TAIL_BLAZER: 5}], [{TAIL_BLAZER: 5}], 0
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
        map=map, players_info=(player_info_1, player_info_2), first_turn=Side.MOUSE
    )
    # endregion

    backend_adapter = BackendAdapter(
        game_manager=game_manager, coordination_manager=coordination_manager
    )

    coordination_manager.put_message(
        PageNavigationEvent(
            action_list=[(PageNavigation.OPEN, "InspectCrumb")]
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
