DIAG: float = 225
SCREEN_RATIO: tuple[float, float] = (4, 3)  # 4:3 width to height ratio

SCREEN_SIZE: tuple[float, float] = (
    SCREEN_RATIO[0] * DIAG,
    SCREEN_RATIO[1] * DIAG,
)
SCREEN_SIZE_HALVED: tuple[float, float] = (SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 2)
THEME_PATH: str = ""
