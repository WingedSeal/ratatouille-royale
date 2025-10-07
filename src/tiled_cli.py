from json import load
from pathlib import Path
from ratroyale.backend import tiled_tmj
import sys


def tiled_to_rrmap(map_name: str) -> None:
    with Path("rrmap.tmj").open("r") as f:
        map = tiled_tmj.tmj_to_map(load(f), map_name)
    map.to_file(Path(f"{map_name.lower().replace(' ', '-')}.rrmap"))


def gen_tileset(size: str, old_tileset_image: str | None = None) -> None:
    if "x" not in size:
        print("Size must be in format ROWxCOL, e.g., 10x10")
        sys.exit(1)

    row, col = map(int, size.lower().split("x"))
    if old_tileset_image is None:
        tiled_tmj.gen_tileset_tsx(row, col)
    else:
        tiled_tmj.gen_tileset_tsx(row, col, old_tileset_image)


def reset() -> None:
    tiled_tmj.reset_toolkit()


def main() -> None:
    cmd, *args = sys.argv[1:]
    if cmd == "to-rrmap":
        if len(args) != 1:
            print("Usage: tiled-cli to-rrmap <map_name>")
            sys.exit(1)
        tiled_to_rrmap(args[0])
    elif cmd == "gen-tileset":
        if len(args) not in (1, 2):
            print("Usage: tiled-cli gen-tileset <row>x<col> [old_tileset_image]")
            sys.exit(1)
        gen_tileset(*args)
    elif cmd == "reset":
        reset()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
