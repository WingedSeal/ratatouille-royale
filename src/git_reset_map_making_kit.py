import os
import subprocess
import sys


def main() -> None:
    print("WARNING: This will discard all changes in rrmap-making-kit directory.")
    confirm = input("Continue? (y/N): ")

    if confirm.lower() != "y":
        print("Aborted.")
        sys.exit(1)

    poe_root = os.environ.get("POE_ROOT", ".")
    path = f"{poe_root}/Tiled/rrmap-making-kit"

    subprocess.run(["git", "checkout", "HEAD", "--", path], check=True)
    subprocess.run(["git", "clean", "-fd", path], check=True)


if __name__ == "__main__":
    main()
