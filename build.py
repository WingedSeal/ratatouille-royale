from setuptools import Extension
from Cython.Build import cythonize
from pathlib import Path
import os
import shutil

from setuptools.dist import Distribution
from setuptools.command.build_ext import build_ext

SOURCE_DIR = Path(__file__).parent / "src"
TEMP_BUILD_DIR = Path("temp_cython_build")
SOURCE_EXTENSIONS = (".c", ".cpp")
COMPILED_EXTENSIONS = (".so", ".pyd", ".dll")

#
# def clean_build_artifacts() -> None:
#
#     for file_path in SOURCE_DIR.rglob("*"):
#         if not file_path.is_file():
#             continue
#
#         if file_path.suffix in SOURCE_EXTENSIONS:
#             file_path.unlink()
#         elif file_path.suffix in COMPILED_EXTENSIONS:
#             try:
#                 file_path.relative_to(TEMP_BUILD_DIR)
#                 continue
#             except ValueError:
#                 pass
#             file_path.unlink()
#
#     if TEMP_BUILD_DIR.exists():
#         shutil.rmtree(TEMP_BUILD_DIR)
#


def compile_cython_files() -> None:
    # clean_build_artifacts()
    pyx_files = [f for f in SOURCE_DIR.rglob("*.pyx") if not f.name.startswith("_")]
    if not pyx_files:
        return

    extensions: list[Extension] = []

    module_paths: dict[str, Path] = {}

    for pyx_file in pyx_files:
        module_name = str(pyx_file.relative_to(SOURCE_DIR).with_suffix("")).replace(
            os.sep, "."
        )

        module_paths[module_name] = pyx_file.parent

        extensions.append(
            Extension(
                module_name,
                [pyx_file.as_posix()],
            )
        )

    cythonized_extensions = cythonize(
        extensions,
        compiler_directives={"language_level": "3"},
    )

    dist = Distribution({"ext_modules": cythonized_extensions})
    cmd = build_ext(dist)
    cmd.build_lib = TEMP_BUILD_DIR.as_posix()
    cmd.ensure_finalized()
    cmd.run()
    for module_name, target_dir in module_paths.items():
        search_path = TEMP_BUILD_DIR / Path(module_name.replace(".", os.sep)).parent
        target_dir.mkdir(parents=True, exist_ok=True)
        if not search_path.is_dir():
            continue
        module_stem = module_name.split(".")[-1]
        for source_file in search_path.iterdir():
            if not source_file.is_file():
                continue
            if not source_file.stem.startswith(module_stem):
                continue
            if source_file.suffix not in COMPILED_EXTENSIONS:
                continue
            destination_file = target_dir / source_file.name
            shutil.copy2(source_file, destination_file)
            break

    if TEMP_BUILD_DIR.exists():
        shutil.rmtree(TEMP_BUILD_DIR)


if __name__ == "__main__":
    compile_cython_files()
