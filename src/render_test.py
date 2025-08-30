import pygame
from ratroyale.input.gui_manager import GUIManager
from ratroyale.input.page.page_factory import PageConfigOptions
from ratroyale.utils import EventQueue

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    gui_callback_queue = EventQueue[str]()

    gui_manager = GUIManager(screen=screen, gui_callback_queue=gui_callback_queue)
    gui_manager.push_page("MAIN_MENU")

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # delta time in seconds

        while not gui_callback_queue.empty():
            gui_manager.execute_callbacks()

        screen.fill((0, 0, 0))
        gui_manager.handle_events()
        gui_manager.update(dt)
        gui_manager.draw()

        pygame.display.flip()

if __name__ == "__main__":
    main()