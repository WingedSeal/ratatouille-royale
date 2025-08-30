import pygame
from ratroyale.input.gui_manager import GUIManager
from ratroyale.input.page.page_factory import PageConfigOptions

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    gui_manager = GUIManager(screen)
    gui_manager.push_page("TEST_SWAP")

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # delta time in seconds

        screen.fill((0, 0, 0))
        gui_manager.handle_events()
        gui_manager.update(dt)
        gui_manager.draw()

        pygame.display.flip()

if __name__ == "__main__":
    main()