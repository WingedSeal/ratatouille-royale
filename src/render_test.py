import pygame
from ratroyale.input.page.page_manager import PageManager
from ratroyale.input.input_manager import InputManager
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.input.page.page_config import PageName

from ratroyale.backend.game_manager import GameManager
from ratroyale.backend.map import Map
from ratroyale.backend.player_info.player_info import PlayerInfo
from ratroyale.backend.tile import Tile
from ratroyale.backend.hexagon import OddRCoord
from ratroyale.backend.entities.rodents.vanguard import TailBlazer
from ratroyale.backend.entity import Entity
from ratroyale.backend.side import Side
from ratroyale.backend.player_info.squeak_set import SqueakSet



def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    coordination_manager = CoordinationManager()

    page_manager = PageManager(screen=screen, coordination_manager=coordination_manager)
    input_manager = InputManager(coordination_manager=coordination_manager)

    # region GAME MANAGER DOMAIN 
    size_x, size_y = 5, 8
    tiles: list[list[Tile]] = []
    for q in range(5):
        row = []
        for r in range(5):
            tile = Tile(
                coord=OddRCoord(q, r),
                entities=[],
                height=0,
                features=[]
            )
            row.append(tile)
        tiles.append(row)
    entities: list[Entity] = [TailBlazer(OddRCoord(1,3))]
    
    map = Map(size_x=size_x, size_y=size_y, tiles=tiles, entities=entities, features=[])
    game_manager = GameManager(map=map, 
                               players_info=(
                                   PlayerInfo(squeak_set=SqueakSet()), 
                                   PlayerInfo(squeak_set=SqueakSet())), 
                                first_turn=Side.MOUSE,
                                coordination_manager=coordination_manager)
    # endregion

    page_manager.push_page(PageName.MAIN_MENU)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # delta time in seconds

        while not coordination_manager.all_mailboxes_empty():
            page_manager.execute_callbacks()
            input_manager.execute_callbacks()
            game_manager.execute_callbacks()

        screen.fill((0, 0, 0))
        page_manager.handle_events()
        page_manager.update(dt)
        page_manager.draw()

        pygame.display.flip()

if __name__ == "__main__":
    main()