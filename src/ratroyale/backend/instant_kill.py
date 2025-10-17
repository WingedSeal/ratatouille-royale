from typing import Self


class InstantKill:
    "Sentinel value for damage"

    _instance: None | Self = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


INSTANT_KILL = InstantKill()
