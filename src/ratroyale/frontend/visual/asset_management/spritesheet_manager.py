from .game_obj_to_sprite_registry import SpritesheetMetadata
from pathlib import Path
import pygame
from dataclasses import dataclass, field


@dataclass
class CachedSpritesheet:
    """Immutable repository of a spritesheet’s frames and metadata."""

    spritesheet_key: str
    sprite_size: tuple[int, int]
    animation_list: dict[str, list[int]]  # e.g. {"IDLE": [0,1,2,3]}
    frame_rate: float
    scale: tuple[float, float] = (1.0, 1.0)

    _frames: list[pygame.Surface] = field(default_factory=list)

    def load_spritesheet(self, path: Path) -> None:
        """Load the spritesheet image and slice it into frames."""
        sheet = pygame.image.load(path).convert_alpha()
        sheet_width, sheet_height = sheet.get_size()
        frame_w, frame_h = self.sprite_size

        frames = []
        for y in range(0, sheet_height, frame_h):
            for x in range(0, sheet_width, frame_w):
                frame = sheet.subsurface(pygame.Rect(x, y, frame_w, frame_h)).copy()
                if self.scale != (1.0, 1.0):
                    frame = pygame.transform.scale(
                        frame,
                        (int(frame_w * self.scale[0]), int(frame_h * self.scale[1])),
                    )
                frames.append(frame)

        self._frames = frames

    def get_sprite_by_abs_index(self, abs_index: int) -> pygame.Surface:
        if not self._frames:
            raise ValueError("Spritesheet not loaded yet")
        return self._frames[abs_index]

    def get_sprite_by_name(self, anim_name: str, frame_index: int) -> pygame.Surface:
        indices = self.animation_list.get(anim_name)
        if indices is None:
            raise ValueError(f"Animation '{anim_name}' not found")
        abs_index = indices[frame_index % len(indices)]
        return self.get_sprite_by_abs_index(abs_index)

    def get_key(self) -> str:
        return self.spritesheet_key


# TODO: lazy loading & unloading unused frames for mem efficiency
class SpritesheetManager:
    """Central manager for cached spritesheets."""

    _cached_spritesheets: dict[str, CachedSpritesheet] = {}

    @classmethod
    def register_spritesheet(cls, metadata: SpritesheetMetadata) -> CachedSpritesheet:
        """Load and register a spritesheet by key."""
        if metadata.key in cls._cached_spritesheets:
            return cls._cached_spritesheets[metadata.key]

        sheet = CachedSpritesheet(
            spritesheet_key=metadata.key,
            sprite_size=metadata.sprite_size,
            animation_list=metadata.animation_list,
            frame_rate=metadata.frame_rate,
            scale=metadata.scale,
        )
        sheet.load_spritesheet(metadata.path)
        cls._cached_spritesheets[metadata.key] = sheet
        return sheet

    @classmethod
    def get_spritesheet(cls, key: str) -> CachedSpritesheet:
        """Retrieve a cached spritesheet by key."""
        result = cls._cached_spritesheets.get(key)
        if not result:
            raise KeyError(f"Spritesheet with {key} not found.")
        return result

    @classmethod
    def unregister_spritesheet(cls, key: str) -> None:
        """Remove a spritesheet from the cache."""
        if key in cls._cached_spritesheets:
            del cls._cached_spritesheets[key]

    @classmethod
    def clear(cls) -> None:
        """Clear all cached spritesheets."""
        cls._cached_spritesheets.clear()

    @classmethod
    def get_frame_count(cls, key: str, anim_name: str) -> int:
        spritesheet = cls.get_spritesheet(key)
        if not spritesheet:
            raise TypeError(f"Spritesheet with name {key} not found.")

        return len(spritesheet.animation_list[anim_name])
