import pygame
from ratroyale.render.page.main_menu_page import MainMenuPage
from ratroyale.render.visual_manager import VisualManager

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    visual_manager = VisualManager(screen)
    visual_manager.set_active_page("main_menu")

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # delta time in seconds

        screen.fill((0, 0, 0))
        visual_manager.handle_events()
        visual_manager.update(dt)
        visual_manager.draw()

        pygame.display.flip()

if __name__ == "__main__":
    main()