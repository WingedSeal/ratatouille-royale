from .squeak import Squeak


class SqueakSet:
    deck: list[Squeak]

    def __init__(self, deck: list[Squeak]) -> None:
        self.deck = deck
