import pygame

# Should actually be floats but I don't have the energy to deal with this right now.
DIAG: int = 300
SCREEN_RATIO: tuple[int, int] = (4, 3)  # 4:3 width to height ratio

SCREEN_SIZE: tuple[int, int] = (
    SCREEN_RATIO[0] * DIAG,
    SCREEN_RATIO[1] * DIAG,
)
SCREEN_SIZE_HALVED: tuple[int, int] = (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2)
THEME_PATH: str = ""
screen_rect = pygame.Rect((0, 0), SCREEN_SIZE)

# SQUEAK INFO

SQUEAK_COST_PADDING = 5  # padding for cost text

SQUEAK_SIZE = (112, 70)
SQUEAK_MARGIN_FROM_TOPLEFT = (0, 80)
SQUEAK_SPACING = 5

SQUEAK_RECT = pygame.Rect(*SQUEAK_MARGIN_FROM_TOPLEFT, *SQUEAK_SIZE)
