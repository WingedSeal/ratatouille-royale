import pygame
from ratroyale.visual.asset_management.game_obj_to_sprite_registry import SpriteRegistryKey

# TODO: refactor entity/tile sprite drawing into type-based handlers

# region PLACEHOLDER VISUALS

pygame.font.init()
DEFAULT_FONT = pygame.font.SysFont(None, 16)


def make_labeled_box(
    size: tuple[int, int],
    color: tuple[int, int, int, int],
    label: str,
    font: pygame.font.Font = DEFAULT_FONT,
) -> pygame.Surface:
    box_width, box_height = size

    # Render the label
    text_surf = font.render(label, True, (255, 255, 255))
    text_width, text_height = text_surf.get_size()

    # Make the surface wide enough to fit the text
    surf_width = max(box_width, text_width)
    surf_height = box_height + text_height
    surf = pygame.Surface((surf_width, surf_height), pygame.SRCALPHA)

    # Draw the box centered horizontally
    box_x = (surf_width - box_width) // 2
    box_surf = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
    box_surf.fill(color)
    surf.blit(box_surf, (box_x, 0))

    # Draw the label centered under the box
    text_rect = text_surf.get_rect(
        center=(surf_width // 2, box_height + text_height // 2)
    )
    surf.blit(text_surf, text_rect)

    return surf


def make_surface(
    size: tuple[int, int],
    color: tuple[int, int, int] | tuple[int, int, int, int],
    border_thickness: int = 3,
) -> pygame.Surface:
    surf = pygame.Surface(size, pygame.SRCALPHA)

    surf.fill(color)

    def darker(
        c: tuple[int, int, int, int] | tuple[int, int, int],
    ) -> tuple[int, int, int, int]:
        # Ensure c has 4 elements (RGBA)
        if len(c) == 3:
            r, g, b = c
            a = 255
        else:
            r, g, b, a = c

        factor = 0.6  # darken by 40%
        return (int(r * factor), int(g * factor), int(b * factor), a)

    border_color = darker(color)

    # Draw the border rectangle
    pygame.draw.rect(surf, border_color, surf.get_rect(), border_thickness)

    return surf


# endregion

TYPICAL_TILE_SIZE = (64, 64)

SPRITE_REGISTRY = {
    SpriteRegistryKey.DEFAULT_TILE: make_surface(TYPICAL_TILE_SIZE, (0, 255, 0, 128)),
    SpriteRegistryKey.DEFAULT_ENTITY: make_surface((32, 32), (255, 0, 0, 255)),
    SpriteRegistryKey.RODENT_TAILBLAZER: make_labeled_box(
        (32, 32), (255, 0, 0, 255), "TailBlazer"
    ),
}
