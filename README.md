# Quantum-robot Python Package

<div align="center" style="align:center; padding:20px">
    <a href="http://quantum-robot.org">
        <img width="300" src="https://raw.githubusercontent.com/Davidelanz/quantum-robot/master/docs/quantum-robot-logo.svg">
    </a>
</div>

<div align="center" style="align:center; padding:20px; line-height:2;">
    <a href="https://travis-ci.com/github/Davidelanz/quantum-robot">
        <img src="https://travis-ci.com/Davidelanz/quantum-robot.svg?branch=master" alt="Build"/>
    </a>
    <a href="https://github.com/Davidelanz/quantum-robot/actions/workflows/python-package.yml">
        <img src="https://github.com/Davidelanz/quantum-robot/actions/workflows/python-package.yml/badge.svg"/>
    </a>
    <a href='http://docs.quantum-robot.org/en/latest/?badge=latest'>
        <img src='https://readthedocs.org/projects/quantum-robot/badge/?version=latest' alt='Documentation Status' />
    </a>
    <a href="https://frontend.code-inspector.com/public/project/13599/quantum-robot/dashboard">
        <img src="https://www.code-inspector.com/project/13599/score/svg" alt="Code Quality"/>
    </a>
    <a href="https://codecov.io/gh/Davidelanz/quantum-robot" >
        <img src="https://codecov.io/gh/Davidelanz/quantum-robot/branch/master/graph/badge.svg?token=69IQEINMQU" alt="Code coverage"/>
    </a>
    <a href="https://codeclimate.com/github/Davidelanz/quantum-robot/maintainability">
        <img src="https://api.codeclimate.com/v1/badges/498a54bb981af54decec/maintainability" alt="Maintainability"/>
    </a>
    <a href="https://github.com/Davidelanz/quantum-robot/actions/workflows/codeql-analysis.yml">
        <img src="https://github.com/Davidelanz/quantum-robot/actions/workflows/codeql-analysis.yml/badge.svg" alt="Maintainability"/>
    </a>
    <a>
        <!--python-&#8805;3.7-->
         <img src="https://img.shields.io/badge/python-3.7|3.8-blue" alt="Python"/>
    </a>
    <a href="https://pypi.org/project/quantum-robot/">
        <img src="https://badge.fury.io/py/quantum-robot.svg" alt="PyPi version"/>
    </a>
    <a href="https://pypi.org/project/quantum-robot/">
        <img src="https://pypip.in/status/quantum-robot/badge.svg" alt="Development Status"/>
    </a>
    <a href="https://github.com/Davidelanz/quantum-robot/blob/master/LICENSE">
        <img src="https://img.shields.io/badge/license-GNU_GPL_v3-blue" alt="License"/>
    </a>
    <a href="https://zenodo.org/badge/latestdoi/274185290">
        <img src="https://zenodo.org/badge/274185290.svg" alt="DOI">
    </a>
</div>

`quantum-robot` is a Python package for quantum-like perception modeling
for robotics. The package exploits [Qiksit](https://qiskit.org/)
framework, implementing the models on quantum circuits which can be
simulated on a classical computer or sent to a quantum backend (service
provided by [IBM Quantum
Experience](https://quantum-computing.ibm.com/)).

The project was started in 2019 by
[Davide Lanza](https://scholar.google.com/citations?user=Lqx6VqEAAAAJ)
as a Master thesis
research, with the help of
[Fulvio Mastrogiovanni](https://scholar.google.it/citations?user=9dRRzV0AAAAJ&hl=en)
and
[Paolo Solinas](https://rubrica.unige.it/personale/UkNHWllv).

It is currently maintained by [Davide Lanza](https://scholar.google.com/citations?user=Lqx6VqEAAAAJ).

- Website: <http://quantum-robot.org>
- Repository: <https://github.com/Davidelanz/quantum-robot/>
- Documentation: <http://docs.quantum-robot.org/en/latest/>

## Contents

- [Install](#install)
- [Notebooks](#notebooks)
- [Contributing](#contributing)
- [Citing](#citing)
- [License](#license)

## Install[↑](#contents)

Check the
[Getting Started](http://docs.quantum-robot.org/en/latest/getting_started/getting_started.html)
section of the Documentation

## Notebooks[↑](#contents)

Several [notebooks](https://github.com/Davidelanz/quantum-robot/tree/master/notebooks) are availabe, to get started with the package and its
capabilities:

- [One-dimensional demo for the
  AngularModel](https://github.com/Davidelanz/quantum-robot/blob/master/notebooks/demo_angular_dim1.ipynb).
- [Three-dimensional demo for the
  AngularModel](https://github.com/Davidelanz/quantum-robot/blob/master/notebooks/demo_angular_dim3_rgb.ipynb).
- [Computation speed analysis for the
  AngularModel](https://github.com/Davidelanz/quantum-robot/blob/master/notebooks/computation_speed.ipynb).
- [One-dimensional comparison between AngularModel and
  LinearModel](https://github.com/Davidelanz/quantum-robot/blob/master/notebooks/model_comparison.ipynb).
- [Tutorial: how to use QUnits](https://github.com/Davidelanz/quantum-robot/blob/master/notebooks/tutorial_qunits.ipynb) (in progress)

## Contributing [↑](#contents)

If you are interested in the project, we welcome new contributors of all
experience levels. For any question, [contact the
maintainer](mailto:lanza.davide.it@gmail.com).

An example module with the docstring standard we adopted is available
[here](https://github.com/Davidelanz/quantum-robot/blob/master/docs/docstring_example/template.py).

## Citing [↑](#contents)

If you use quantum-robot in a scientific publication, we would
appreciate citations to the following paper:

```{.sourceCode .bibtex}
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

## License [↑](#contents)

[GNU-GPLv3](https://github.com/Davidelanz/quantum-robot/blob/master/LICENSE)
