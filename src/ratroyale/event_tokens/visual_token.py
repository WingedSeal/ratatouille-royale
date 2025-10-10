from dataclasses import dataclass

from .base import EventToken

# TODO: figure the visual domain out more concretely.


@dataclass
class VisualManagerEvent(EventToken):
    pass
