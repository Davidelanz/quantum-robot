"""Format Python cells in the MyST notebooks through Jupytext and Ruff."""

import argparse
import difflib
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
from tempfile import gettempdir, TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = sorted((ROOT / "docs" / "notebooks").glob("[0-9][0-9]_*.md"))


def _format(notebook: Path) -> None:
    """Format one text notebook in place."""
    ruff = f"{shlex.quote(sys.executable)} -m ruff format -"
    jupyter_root = Path(gettempdir()) / "qrobot-jupyter-format"
    jupyter_environment = {
        **os.environ,
        "IPYTHONDIR": str(jupyter_root / "ipython"),
        "JUPYTER_CONFIG_DIR": str(jupyter_root / "config"),
        "JUPYTER_DATA_DIR": str(jupyter_root / "data"),
        "JUPYTER_RUNTIME_DIR": str(jupyter_root / "runtime"),
    }
    for variable in (
        "IPYTHONDIR",
        "JUPYTER_CONFIG_DIR",
        "JUPYTER_DATA_DIR",
        "JUPYTER_RUNTIME_DIR",
    ):
        Path(jupyter_environment[variable]).mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            sys.executable,
            "-m",
            "jupytext",
            "--pipe-fmt",
            "py:percent",
            "--pipe",
            ruff,
            str(notebook),
        ],
        check=True,
        cwd=ROOT,
        env=jupyter_environment,
    )


def _check() -> int:
    """Return nonzero and print diffs when formatting would change a notebook."""
    changed = False
    with TemporaryDirectory(prefix="qrobot-notebook-format-") as temporary:
        temporary_directory = Path(temporary)
        for notebook in NOTEBOOKS:
            candidate = temporary_directory / notebook.name
            shutil.copyfile(notebook, candidate)
            _format(candidate)
            original_text = notebook.read_text()
            formatted_text = candidate.read_text()
            if original_text == formatted_text:
                continue
            changed = True
            sys.stdout.writelines(
                difflib.unified_diff(
                    original_text.splitlines(keepends=True),
                    formatted_text.splitlines(keepends=True),
                    fromfile=str(notebook.relative_to(ROOT)),
                    tofile=f"{notebook.relative_to(ROOT)} (formatted)",
                )
            )
    if changed:
        print("Notebook code cells need formatting.", file=sys.stderr)
        return 1
    print(f"{len(NOTEBOOKS)} MyST notebooks already formatted.")
    return 0


def main() -> int:
    """Format notebooks or verify their formatting."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="report formatting differences without changing source files",
    )
    arguments = parser.parse_args()
    if not NOTEBOOKS:
        parser.error("no numbered MyST notebooks found")
    if arguments.check:
        return _check()
    for notebook in NOTEBOOKS:
        _format(notebook)
    print(f"Formatted {len(NOTEBOOKS)} MyST notebooks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
