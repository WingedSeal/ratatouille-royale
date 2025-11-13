import pygame

from ratroyale.backend.features.common import DeploymentZone, Lair
from ratroyale.backend.hexagon import OddRCoord
from ratroyale.backend.map import Map, heights_to_tiles
from ratroyale.backend.side import Side
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.page_token import PageNavigation, PageNavigationEvent
from ratroyale.frontend.visual.screen_constants import SCREEN_SIZE

from .frontend.pages.page_managers.page_manager import PageManager


def __temp_get_map() -> Map:
    size = 10
    return Map(
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
                shape=[
                    OddRCoord(size - 2, size - 1),
                    OddRCoord(size - 1, size - 2),
                ],
                side=Side.RAT,
            ),
        ],
    )


MILLISECOND_PER_SECOND = 1000


class Game:
    """
    The entry-point and the controller class
    """

    FPS_ALPHA = 0.1
    """Smoothing factor for calculating average FPS"""
    MAX_FPS = 60

    def __init__(self) -> None:
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.clock = pygame.time.Clock()
        self.coordination_manager = CoordinationManager()
        self.page_manager = PageManager(
            screen=self.screen, coordination_manager=self.coordination_manager
        )
        self.average_fps: float = 0.0

    def run(self) -> None:
        self.coordination_manager.put_message(
            PageNavigationEvent(
                action_list=[
                    (PageNavigation.OPEN, "MainMenu"),
                ]
            )
        )

        while self.coordination_manager.game_running:
            dt = self.clock.tick(self.MAX_FPS) / MILLISECOND_PER_SECOND
            self.update(dt)
            current_fps = self.clock.get_fps()
            if current_fps > 0:
                self.average_fps = (
                    1 - self.FPS_ALPHA
                ) * self.average_fps + self.FPS_ALPHA * current_fps

        pygame.quit()

    def update(self, dt: float) -> None:
        self.screen.fill((0, 0, 0))
        self.page_manager.handle_events()

        while not self.coordination_manager.all_mailboxes_empty():
            self.page_manager.execute_page_callback()
            self.page_manager.execute_visual_callback()
            self.page_manager.execute_backend_page_callback()

        self.page_manager.render(dt)
        pygame.display.flip()
