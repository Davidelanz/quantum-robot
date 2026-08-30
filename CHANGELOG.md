# Changelog

All notable changes are documented here. Semantic Versioning starts with 1.0.0.

## [1.0.0] - 2026-08-30

This release deliberately defines a new API. Compatibility with the published
0.1 alpha is not a goal; see the migration notes below.

The comparison baseline for this section is the unreleased `master` snapshot
from 2023-06-13 described in the next section.

### Added

- Added the `QuantumBackend` interface and bundled `QiskitBackend` for current
  Qiskit releases.
- Added opt-in application logging in `qrobot.logger`.
- Added `ActuatorUnit` to the Redis-backed qUnit system.
- Added experimental grasping-robot and predator/prey simulators, runnable
  examples, and executable tutorials.
- Added normalized scalar and vector inputs to `QUnit`, `SensorialUnit`, and
  `ActuatorUnit`.
- Added a glossary, NumPy docstring validation, strict mypy checks, and separate
  core and extension test organization.

### Changed

- Split optional capabilities out of the core namespace: `qrobot.qunits` became
  `qrobot_qunits`, graph/drawing tools became `qrobot_visualization`, and the
  dashboard became `qrobot_dashboard`; the new simulator uses
  `qrobot_simulator`.
- Made model plotting, Redis integration, visualization, simulation, and the
  dashboard optional install extras in the single `quantum-robot` distribution.
- Renamed the qUnit sampling interval from `Ts` to `sampling_period`.
- Made visualization functions return figure objects and replaced `graph` as the
  network-construction entry point with `build_network`.
- Replaced the internal Qiskit execution path with the new backend boundary.
- Replaced RST pages and Jupyter notebook sources with executable MyST Markdown.
- Updated the build, dependencies, documentation, and CI for Python 3.14.

### Fixed

- Fixed target-vector dimension validation and density-matrix construction in
  the models.
- Fixed qUnit fallback-input preservation, worker lifecycle, Redis injection,
  worker logging, and input normalization.
- Fixed dashboard construction when Redis contains partial network state.

### Deprecated

- Nothing. Version 1.0.0 is a clean API boundary rather than a compatibility
  transition.

### Removed

- Removed the old nested extension import paths under `qrobot`.
- Removed the obsolete Docker development setup and legacy RST/Jupyter sources.
- Removed support for Python versions earlier than 3.14.

### Migration from the 2023 master snapshot

- Replace `qrobot.qunits` imports with `qrobot_qunits` and install the `qunits`
  extra.
- Replace `qrobot.draw` and `qrobot.graph` imports with
  `qrobot_visualization` and install the `visualization` extra.
- Replace `qrobot.dashboard` imports with `qrobot_dashboard` and install the
  `dashboard` extra.
- Replace qUnit constructor keyword `Ts=` with `sampling_period=`.
- Replace network construction through `graph(...)` with `build_network(...)`;
  drawing functions now return their figure objects.
- Configure desired logging explicitly with `qrobot.logger.configure_logging`.

## Master snapshot (unreleased) - 2023-06-13

> **Historical note:** this is commit
> [`d797c1a`](https://github.com/Davidelanz/quantum-robot/commit/d797c1a8e943a3201ea523bd031131549718b06c),
> the tip of `master` on 2023-06-13. It was never tagged or published to PyPI
> and is not a package version. It is recorded solely as an intermediate
> baseline between the published 0.1 alpha and 1.0.0.

### Added

- Added Redis-backed `QUnit` and `SensorialUnit` components, multiprocessing-safe
  inputs and outputs, worker logging, network status data, and burst-output
  retrieval.
- Added burst strategies as `Burst`, `OneBurst`, and `ZeroBurst`.
- Added Redis network graph generation and drawing tools.
- Added an early Dash dashboard and factory-based application construction.
- Added Poetry packaging, a `src/` layout, Redis-enabled tests, GitHub Actions,
  CodeQL, Read the Docs configuration, Docker development files, and expanded
  tutorials and project documentation.

### Changed

- Refactored the original models and package structure for Python 3.8 or later.
- Replaced the early ROS/roscore architecture with Redis-based communication.
- Moved all runtime dependencies into Poetry metadata; at this snapshot they
  were still mandatory rather than extras.

### Fixed

- Fixed burst counting and byte/string decoding inherited from 0.1.
- Fixed model, qUnit multiprocessing, Redis serialization, output retrieval,
  tests, documentation, and CI issues during development of the snapshot.

### Deprecated

- Nothing was formally deprecated in this unreleased snapshot.

### Removed

- Removed `BurstAModel` in favor of separate model and burst strategy classes.
- Removed setuptools/`requirements.txt` packaging and the original top-level
  source layout.

## [0.1] - 2020-07-01

### Added

- Initial alpha release of `Model`, `LinearModel`, `AngularModel`, and
  `BurstAModel`, with first tests and documentation.
- NumPy, Qiskit, pandas, Matplotlib, and seaborn as mandatory dependencies.

[1.0.0]: https://github.com/Davidelanz/quantum-robot/compare/d797c1a8e943a3201ea523bd031131549718b06c...1.0.0
[0.1]: https://github.com/Davidelanz/quantum-robot/releases/tag/0.1
