"""Check that NumPy docstring parameters match Python signatures."""

from __future__ import annotations

import argparse
import ast
from pathlib import Path
import re
import sys

SECTION_UNDERLINE = re.compile(r"^-{3,}$")
PARAMETER_ENTRY = re.compile(r"^([*\w][\w\s, *]*)\s*:\s*.+$")


def _signature_parameters(node: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    """Return the documentable parameter names in a function signature."""
    arguments = [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
    names = {argument.arg for argument in arguments if argument.arg not in {"self", "cls"}}
    if node.args.vararg:
        names.add(node.args.vararg.arg)
    if node.args.kwarg:
        names.add(node.args.kwarg.arg)
    return names


def _documented_parameters(docstring: str) -> set[str] | None:
    """Return names in a NumPy ``Parameters`` section, if one exists."""
    lines = docstring.splitlines()
    for index, line in enumerate(lines[:-1]):
        if line.strip() != "Parameters" or not SECTION_UNDERLINE.fullmatch(
            lines[index + 1].strip()
        ):
            continue

        names: set[str] = set()
        for entry in lines[index + 2 :]:
            match = PARAMETER_ENTRY.match(entry)
            if match:
                names.update(name.strip().lstrip("*") for name in match.group(1).split(","))
            elif entry and not entry[0].isspace():
                break
        return names
    return None


def check_file(path: Path) -> list[str]:
    """Return signature-to-docstring parameter mismatches in ``path``."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    errors: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        docstring = ast.get_docstring(node)
        if not docstring:
            continue
        expected = _signature_parameters(node)
        documented = _documented_parameters(docstring)
        if documented is None:
            continue
        missing = expected - documented
        extra = documented - expected
        if missing:
            errors.append(
                f"{path}:{node.lineno}: {node.name}: undocumented parameter(s): "
                f"{', '.join(sorted(missing))}"
            )
        if extra:
            errors.append(
                f"{path}:{node.lineno}: {node.name}: unknown documented parameter(s): "
                f"{', '.join(sorted(extra))}"
            )
    return errors


def main() -> int:
    """Check Python files below the supplied paths."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    files = sorted(
        file for path in args.paths for file in ([path] if path.is_file() else path.rglob("*.py"))
    )
    errors = [error for file in files for error in check_file(file)]
    if errors:
        print("\n".join(errors))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
