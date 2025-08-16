from .render.renderer import Renderer


class Game:
    """
    The entry-point and the controller class 
    """
    renderer: Renderer

    def __init__(self) -> None:
        self.renderer = Renderer()
        pass

    def run(self) -> None:
        pass
