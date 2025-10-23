from setuptools import Extension
from Cython.Build import cythonize
from pathlib import Path


def build(setup_kwargs) -> None:
    print("BUILDING!")
    pyx_files = [f for f in Path("src").rglob("*.pyx") if not f.name.startswith("_")]

    if not pyx_files:
        return

    extensions = []
    for pyx_file in pyx_files:
        relative_path = pyx_file.relative_to("src")
        module_name = str(relative_path.with_suffix("")).replace("/", ".")

        extensions.append(
            Extension(
                module_name,
                [str(pyx_file)],
                extra_compile_args=["-O3"],
            )
        )

    setup_kwargs.update(
        {
            "ext_modules": cythonize(
                extensions,
                compiler_directives={"language_level": "3"},
                annotate=True,
            ),
            "zip_safe": False,
        }
    )
