"""Start the local dashboard with ``python -m qrobot_dashboard``."""

import argparse
from collections.abc import Sequence

from qrobot_dashboard.app import create_app


def parse_args(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse dashboard command-line arguments.

    Parameters
    ----------
    arguments : collections.abc.Sequence[str] or None
        Arguments to parse. When omitted, read them from ``sys.argv``.

    Returns
    -------
    argparse.Namespace
        Parsed host and port values.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", help="Bind address (default: 127.0.0.1).")
    parser.add_argument("--port", type=int, default=8050, help="HTTP port (default: 8050).")
    return parser.parse_args(arguments)


def main(arguments: Sequence[str] | None = None) -> None:
    """Run the dashboard server until interrupted.

    Parameters
    ----------
    arguments : collections.abc.Sequence[str] or None
        Optional command-line arguments used primarily by tests and embedding.
    """
    args = parse_args(arguments)
    create_app().run(host=args.host, port=args.port, debug=False, use_reloader=False)


if __name__ == "__main__":  # pragma: no cover - exercised through ``main``
    main()
