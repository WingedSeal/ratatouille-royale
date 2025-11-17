import black
import re
from pathlib import Path
from ratroyale.backend.map import Map

MAP_DIRECTORY = Path(__file__).parent / "ratroyale/map_file"
MAP_MAKING_KIT_DIRECTORY = Path(__file__).parents[1] / "Tiled/rrmap-making-kit"


def sanitize_repr(repr_string: str):
    repr_string = re.sub(r"<class '([^']+)'>", r"'\1'", repr_string)
    repr_string = re.sub(r"<([^>]+)>", r'"\g<1>"', repr_string)

    return repr_string


def print_info(path: Path) -> None:
    map = Map.from_file(path)
    assert map is not None
    repr_string = repr(map.features)  # Edit Here
    repr_string = sanitize_repr(repr_string)
    print(black.format_str(repr_string, mode=black.Mode()))


def edit_map(path: Path) -> None:
    map = Map.from_file(path)
    assert map is not None
    # Edit Here
    for feature in map.features:
        if feature.shape == [...]:
            feature.side = None

    map.to_file(path)


def main() -> None:
    # path = MAP_DIRECTORY / "starting-kitchen.rrmap"
    path = MAP_MAKING_KIT_DIRECTORY / "starting-kitchen.rrmap"
    print_info(path)
    # edit_map(path)


if __name__ == "__main__":
    main()
