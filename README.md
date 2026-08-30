# quantum-robot

[![Package Check](https://github.com/Davidelanz/quantum-robot/actions/workflows/package-check.yml/badge.svg)](https://github.com/Davidelanz/quantum-robot/actions/workflows/package-check.yml)
[![CodeQL](https://github.com/Davidelanz/quantum-robot/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/Davidelanz/quantum-robot/actions/workflows/codeql-analysis.yml)
[![Code coverage](https://codecov.io/gh/Davidelanz/quantum-robot/branch/master/graph/badge.svg?token=69IQEINMQU)](https://codecov.io/gh/Davidelanz/quantum-robot)
[![Documentation Status](https://readthedocs.org/projects/quantum-robot/badge/?version=latest)](http://docs.quantum-robot.org/en/latest/)
[![Snyk Advisor](https://img.shields.io/badge/Snyk_Security-blue)](https://snyk.io/advisor/python/quantum-robot)
[![Maintainability](https://api.codeclimate.com/v1/badges/498a54bb981af54decec/maintainability)](https://codeclimate.com/github/Davidelanz/quantum-robot/maintainability)
[![License](https://img.shields.io/badge/license-GNU_GPL_v3-blue)](LICENSE)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.3926776-blue)](https://doi.org/10.5281/zenodo.3926776)

`quantum-robot` provides quantum-like perception models for robotics. It
targets Python 3.14 and exposes a small backend interface; Qiskit is the
bundled backend implementation.

The project was started in 2019 by
[Davide Lanza](https://scholar.google.com/citations?user=Lqx6VqEAAAAJ) as
Master's thesis research, with help from
[Fulvio Mastrogiovanni](https://scholar.google.it/citations?user=9dRRzV0AAAAJ&hl=en)
and [Paolo Solinas](https://rubrica.unige.it/personale/UkNHWllv). It is
maintained by Davide Lanza.

The project is one Poetry distribution with a dependency-light `qrobot` core
and optional extension import packages:

| Capability | Install extra | Import package | Status |
| --- | --- | --- | --- |
| Core models and Qiskit backend | — | `qrobot` | Supported |
| qUnits / Redis integration | `qunits` | `qrobot_qunits` | Supported |
| Graph and drawing tools | `visualization` | `qrobot_visualization` | Experimental |
| Lightweight 2-D robot simulator | `simulator` | `qrobot_simulator` | Experimental |
| Dashboard | `dashboard` | `qrobot_dashboard` | Experimental |

> [!WARNING]
> `qrobot_simulator`, `qrobot_visualization`, and `qrobot_dashboard` are
> experimental extensions. Their public interfaces, configuration, and output
> may change between minor releases while their contracts are being defined.

## Install

Install the published core package:

```console
python -m pip install --upgrade quantum-robot
```

Install optional capabilities only when needed:

```console
python -m pip install --upgrade "quantum-robot[model-visualization,qunits,visualization,simulator,dashboard]"
```

Python 3.14 is required. For an isolated installation, create and activate a
virtual environment before running `pip`:

```console
python3.14 -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

See the [getting-started guide](http://docs.quantum-robot.org/en/latest/getting_started/getting_started.html)
for individual extras, Redis setup, and installation checks.

## Development

Use [Poetry](https://python-poetry.org/) with Python 3.14. The following
installs every development capability into Poetry’s project environment:

```console
git clone https://github.com/Davidelanz/quantum-robot.git
cd quantum-robot
poetry env use 3.14
poetry install --all-extras
```

Run the standard quality checks through that environment:

```console
poetry check
poetry run ruff check src tests scripts
poetry run python scripts/check_docstrings.py src
poetry run black --check src tests scripts
poetry run python scripts/format_notebooks.py --check
poetry run mypy src
poetry run pytest --cov=qrobot --cov-fail-under=100
poetry build
```

Apply the formatter when needed:

```console
poetry run black src tests scripts
poetry run python scripts/format_notebooks.py
```

The notebook formatter converts each numbered MyST notebook through Jupytext,
runs Ruff over its Python cells, and writes it back without creating committed
`.ipynb` files.

The qUnits integration tests and the executable qUnits tutorial require Redis
on `localhost:6379`. Start a disposable local instance when running them:

```console
docker run --rm --name qrobot-redis -p 6379:6379 -d redis:7-alpine
poetry run pytest
```

Stop it with `docker stop qrobot-redis`.

Run either of the two embodied examples with Redis listening locally:

```console
poetry run python examples/grasping_robot.py
poetry run python examples/bug_world.py
```

`grasping_robot` presents an approaching ball, distance and touch interfaces,
and a qBrain-controlled gripper. `bug_world` opens a predator/prey chessboard
where the qBrain drives five behavioral actuator interfaces. Both are small
live 2-D simulations; the foundational model demonstrations remain executable
inside the notebooks.

## Documentation

The documentation source is MyST Markdown, including tutorials.
Building it runs those tutorials, renders MathJax formulas, and writes the
resulting site to `docs/_build/html`:

```console
docker run --rm --name qrobot-redis -p 6379:6379 -d redis:7-alpine
poetry run python scripts/build_docs.py
```

Open `docs/_build/html/index.html` directly in a browser.

## Project layout

```text
src/
  qrobot/                 # core package and backend interface
  qrobot_qunits/          # optional Redis-based extension
  qrobot_visualization/   # optional graph/drawing extension
  qrobot_simulator/       # grasping_robot and bug_world 2-D simulators
  qrobot_dashboard/       # optional dashboard extension
examples/                 # exactly two embodied example runners
tests/
  core/
  extensions/
docs/                     # MyST API docs and tutorials
```

## Contributing and citation

Contributions are welcome; see [the contributing guide](.github/CONTRIBUTING.md).
For questions, contact [the maintainer](mailto:info@davidelanza.it).

If you use quantum-robot in research, we would
appreciate citations to the following:

``` bibtex
@misc{lanza2020quantum,
    author={Lanza, Davide},
    title={Quantum-like Modeling of Cognitive Architectures for Robotics},
    year={2020},
    publisher={Zenodo},
    doi={10.5281/zenodo.22068511},
    url={https://doi.org/10.5281/zenodo.22068511},
    note={Master's thesis for the EMARO+ (European Master on Advanced Robotics) programme.},
}
@misc{lanza2020preliminary,
    title={Multi-sensory Integration in a Quantum-Like Robot Perception Model},
    author={Davide Lanza and Paolo Solinas and Fulvio Mastrogiovanni},
    year={2020},
    eprint={2006.16404},
    archivePrefix={arXiv},
    primaryClass={cs.RO},
    note={preprint at \url{https://arxiv.org/abs/2006.16404}},
}
```

## License

[GPL-3.0-or-later](LICENSE)
