"""Build the executable HTML documentation from a source checkout."""

import os
from pathlib import Path
from subprocess import run
import sys
from tempfile import gettempdir


def main() -> None:
    """Execute MyST tutorials and build strict Sphinx HTML documentation."""
    root = Path(__file__).resolve().parents[1]
    docs = root / "docs"

    # Keep Jupyter state outside the checkout. This prevents notebook kernels
    # from writing user-specific runtime/configuration files into the project.
    jupyter_tmp = Path(gettempdir()) / "qrobot-jupyter"
    jupyter_tmp.mkdir(exist_ok=True)

    # Matplotlib and Jupyter both write caches; isolate them from source files
    # so a documentation build leaves only the ignored ``docs/_build`` output.
    environment = {
        **os.environ,
        "MPLCONFIGDIR": str(docs / "_build" / ".matplotlib"),
        "JUPYTER_DATA_DIR": str(jupyter_tmp / "data"),
        "JUPYTER_CONFIG_DIR": str(jupyter_tmp / "config"),
        "JUPYTER_RUNTIME_DIR": str(jupyter_tmp / "runtime"),
    }
    run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            "html",
            # Recreate the Sphinx environment so MyST-NB executes every
            # tutorial and refreshes the generated results on each build.
            "-E",
            "-W",
            "--keep-going",
            str(docs),
            str(docs / "_build" / "html"),
        ],
        check=True,
        cwd=root,
        env=environment,
    )


if __name__ == "__main__":
    main()
