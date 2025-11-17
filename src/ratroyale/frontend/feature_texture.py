import pygame
import math
from enum import IntEnum
from pathlib import Path

from ratroyale.backend.hexagon import OddRCoord


class TriangleType(IntEnum):
    FULL_CONNECTED = 0
    """The both triangle edge and nearby edge connect with a neighbor"""
    ISOLATED = 1
    CONNECTED = 2
    """Only the triangle edge connects with a neighbor"""


def _calculate_triangle_points(
    hex_width: float,
    hex_height: float,
    bounding_box_width: float,
    bounding_box_height: float,
) -> list[list[tuple[float, float]]]:
    """
    Triangles starts from east (right) side.
    hex_width and hex_height are the radii (distance from center to vertices).
    """
    triangles: list[list[tuple[float, float]]] = []
    center = bounding_box_width / 2, bounding_box_height / 2
    vertices: list[tuple[float, float]] = []

    for i in range(6):
        angle = math.pi / 3 * i - math.pi / 6
        x = center[0] + hex_width * math.cos(angle)
        y = center[1] + hex_height * math.sin(angle)
        vertices.append((x, y))

    for i in range(6):
        v1 = vertices[i]
        v2 = vertices[(i + 1) % 6]
        mid = ((v1[0] + v2[0]) / 2, (v1[1] + v2[1]) / 2)
        triangles.append([center, v1, mid])
        triangles.append([center, mid, v2])

    return triangles


def _get_triangle_type(
    triangle_index: int, coord: OddRCoord, relative_feature_coords: list[OddRCoord]
) -> TriangleType:
    edge_index = triangle_index // 2
    is_right_triangle = triangle_index % 2 == 1
    neighbors = list(coord.get_neighbors())
    # Convert from right->bottom-right counter-clockwise to right->top-right clockwise
    neighbors = [neighbors[0]] + neighbors[-1:0:-1]
    neighbor_coord = neighbors[edge_index]

    if neighbor_coord not in relative_feature_coords:
        return TriangleType.ISOLATED

    if is_right_triangle:
        adjacent_neighbor_coord = neighbors[(edge_index + 1) % 6]
    else:
        adjacent_neighbor_coord = neighbors[(edge_index - 1) % 6]

    if adjacent_neighbor_coord in relative_feature_coords:
        return TriangleType.FULL_CONNECTED
    else:
        return TriangleType.CONNECTED


def generate_feature_surface(
    origin: OddRCoord,
    relative_feature_coords: list[OddRCoord],
    source_textures: tuple[pygame.Surface, pygame.Surface, pygame.Surface],
    hex_width: float,
    hex_height: float = -1.0,
    *,
    is_bounding_box: bool = False,
) -> pygame.Surface:
    """
    source_textures must be in form of (ISOLATED, CONNECTED, FULL_CONNECTED)
    """
    if hex_height == -1.0:
        hex_height = hex_width

    if is_bounding_box:
        bounding_box_width, bounding_box_height = hex_width, hex_height
        hex_width /= math.sqrt(3)
        hex_height /= 2
    else:
        bounding_box_width = hex_width * math.sqrt(3)
        bounding_box_height = hex_height * 2

    if not relative_feature_coords:
        return pygame.Surface((0, 0), pygame.SRCALPHA)

    is_even_r = origin.y % 2 == 1
    if is_even_r:
        relative_feature_coords = [
            coord + OddRCoord(0, 1) for coord in relative_feature_coords
        ]

    pixel_positions = {
        coord: coord.to_pixel(hex_width, hex_height, is_bounding_box=False)
        for coord in relative_feature_coords
    }

    min_x = min(x for x, _ in pixel_positions.values())
    max_x = max(x for x, _ in pixel_positions.values())
    min_y = min(y for _, y in pixel_positions.values())
    max_y = max(y for _, y in pixel_positions.values())

    surface_width = int(max_x - min_x + bounding_box_width)
    surface_height = int(max_y - min_y + bounding_box_height)
    surface = pygame.Surface((surface_width, surface_height), pygame.SRCALPHA)

    triangle_points = _calculate_triangle_points(
        hex_width, hex_height, bounding_box_width, bounding_box_height
    )

    for coord in relative_feature_coords:
        hex_x, hex_y = pixel_positions[coord]
        offset_x = hex_x - min_x
        offset_y = hex_y - min_y

        for triangle_index in range(12):  # 0=right
            texture_type = _get_triangle_type(
                triangle_index, coord, relative_feature_coords
            )
            source = pygame.transform.scale(
                source_textures[texture_type],
                (int(bounding_box_width), int(bounding_box_height)),
            )
            points = [
                (point[0] + offset_x, point[1] + offset_y)
                for point in triangle_points[triangle_index]
            ]
            mask_surf = pygame.Surface((surface_width, surface_height), pygame.SRCALPHA)
            pygame.draw.polygon(mask_surf, (255, 255, 255, 255), points)
            temp_surf = pygame.Surface((surface_width, surface_height), pygame.SRCALPHA)
            temp_surf.blit(source, (int(offset_x), int(offset_y)))
            temp_surf.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(temp_surf, (0, 0))

    return surface


def load_three_tiles(
    path: Path,
) -> tuple[pygame.Surface, pygame.Surface, pygame.Surface]:
    """
    Load an image containing 3 horizontal 100x100 tiles
    and return a tuple of 3 separate Surfaces.
    """
    full_img = pygame.image.load(path).convert_alpha()

    tile_width = 100
    tile_height = 100

    t0 = pygame.Surface((tile_width, tile_height), pygame.SRCALPHA)
    t0.blit(full_img, (0, 0), pygame.Rect(0, 0, tile_width, tile_height))

    t1 = pygame.Surface((tile_width, tile_height), pygame.SRCALPHA)
    t1.blit(full_img, (0, 0), pygame.Rect(100, 0, tile_width, tile_height))

    t2 = pygame.Surface((tile_width, tile_height), pygame.SRCALPHA)
    t2.blit(full_img, (0, 0), pygame.Rect(200, 0, tile_width, tile_height))

    return (t0, t1, t2)


def __create_example_textures(
    hex_width: int, hex_height: float
) -> tuple[pygame.Surface, pygame.Surface, pygame.Surface]:
    bbox_width = hex_width * math.sqrt(3)
    bbox_height = hex_height * 2

    isolated = pygame.Surface((int(bbox_width), int(bbox_height)), pygame.SRCALPHA)
    isolated.fill((100, 100, 100, 255))

    connected = pygame.Surface((int(bbox_width), int(bbox_height)), pygame.SRCALPHA)
    connected.fill((50, 200, 50, 255))

    nearby = pygame.Surface((int(bbox_width), int(bbox_height)), pygame.SRCALPHA)
    nearby.fill((50, 50, 200, 255))

    return (isolated, connected, nearby)
