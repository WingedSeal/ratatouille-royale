from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pygame_gui.core.ui_element import UIElement
import pygame

class VisualComponent(ABC):
    """Base class for anything that can be rendered as part of an Interactable."""

    @abstractmethod
    def create(self, manager=None):
        """Optional: create/init the visual. 
        For UI, this might need the gui_manager; for sprites, maybe not."""
        pass

    @abstractmethod
    def render(self, surface: pygame.Surface):
        """Draw this visual onto the given surface."""
        pass
    
@dataclass
class UIVisual(VisualComponent):
    type: type[UIElement]
    relative_rect: pygame.Rect
    text: str = ""
    kwargs: dict = field(default_factory=dict)
    instance: UIElement | None = None

    def create(self, manager):
        self.instance = self.type(
            relative_rect=self.relative_rect,
            manager=manager,
            **(self.kwargs or {})
        )

    def render(self, surface: pygame.Surface):
        # pygame_gui handles its own rendering,
        # so this might just be a no-op
        pass
    
class SpriteVisual(VisualComponent):
    image: pygame.Surface
    position: tuple[int, int]

    def create(self, manager=None):
        pass  # nothing to build

    def render(self, surface: pygame.Surface):
        surface.blit(self.image, self.position)