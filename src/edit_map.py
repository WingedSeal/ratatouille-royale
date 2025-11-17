from pathlib import Path
from ratroyale.backend.map import Map

MAP_DIRECTORY = Path(__file__).parent / "ratroyale/map_file"


def main() -> None:
    map = Map.from_file(MAP_DIRECTORY / "starting-kitchen.rrmap")
    assert map is not None
    print(map.features)


if __name__ == "__main__":
    main()
