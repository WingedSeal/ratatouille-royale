import pygame
from ratroyale.input.page.page_manager import PageManager
from ratroyale.input.input_manager import InputManager
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.input.page.page_config import PageName

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    coordination_manager = CoordinationManager()

    page_manager = PageManager(screen=screen, coordination_manager=coordination_manager)
    input_manager = InputManager(coordination_manager=coordination_manager)

    page_manager.push_page(PageName.MAIN_MENU)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # delta time in seconds

        while not coordination_manager.all_mailboxes_empty():
            page_manager.execute_callbacks()
            input_manager.execute_callbacks()

        screen.fill((0, 0, 0))
        page_manager.handle_events()
        page_manager.update(dt)
        page_manager.draw()

        pygame.display.flip()

if __name__ == "__main__":
    main()