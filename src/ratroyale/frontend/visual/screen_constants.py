# Should actually be floats but I don't have the energy to deal with this right now.
DIAG: int = 225
SCREEN_RATIO: tuple[int, int] = (4, 3)  # 4:3 width to height ratio

SCREEN_SIZE: tuple[int, int] = (
    SCREEN_RATIO[0] * DIAG,
    SCREEN_RATIO[1] * DIAG,
)
SCREEN_SIZE_HALVED: tuple[float, float] = (SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 2)
THEME_PATH: str = ""
