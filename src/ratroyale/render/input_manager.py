import pygame

class InputManager:
    """Thin wrapper around pygame event polling"""
    def __init__(self):
        pass

    def update(self):
        return pygame.event.get()