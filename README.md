# Quantum-robot Python Package

<div align="center" style="align:center; padding:20px;">
    <a href="http://quantum-robot.org">
        <img width="300" src="https://raw.githubusercontent.com/Davidelanz/quantum-robot/master/docs/quantum-robot-logo.svg">
    </a>
</div>
<br>
<div align="center" style="align:center; padding:20px; line-height:2;">
    <a href="https://github.com/Davidelanz/quantum-robot/actions/workflows/python-package.yml">
        <img src="https://github.com/Davidelanz/quantum-robot/actions/workflows/python-package.yml/badge.svg"/>
    </a>
    <a href="https://travis-ci.com/github/Davidelanz/quantum-robot">
        <img src="https://travis-ci.com/Davidelanz/quantum-robot.svg?branch=master" alt="Build"/>
    </a>
    <a href='http://docs.quantum-robot.org/en/latest/?badge=latest'>
        <img src='https://readthedocs.org/projects/quantum-robot/badge/?version=latest' alt='Documentation Status' />
    </a>
    <a>
        <img src="https://img.shields.io/badge/python-3.7|3.8|3.9-yellow" alt="Python"/>
    </a>
    <a href="https://github.com/Davidelanz/quantum-robot/actions/workflows/codeql-analysis.yml">
        <img src="https://github.com/Davidelanz/quantum-robot/actions/workflows/codeql-analysis.yml/badge.svg" alt="CodeQL"/>
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
    <a href="https://snyk.io/advisor/python/quantum-robot">
        <img src="https://snyk.io/advisor/python/quantum-robot/badge.svg" alt="snyk">
    </a>
    <a href="https://github.com/Davidelanz/quantum-robot/blob/master/LICENSE">
        <img src="https://img.shields.io/badge/license-GNU_GPL_v3-blue" alt="License"/>
    </a>
    <a href="https://zenodo.org/badge/latestdoi/274185290">
        <img src="https://zenodo.org/badge/274185290.svg" alt="DOI">
    </a>
</div>
<br>

`quantum-robot` is a Python package for quantum-like perception modeling
for robotics. The package exploits [Qiksit](https://qiskit.org/)
framework, implementing the models on quantum circuits which can be
simulated on a classical computer or sent to a quantum backend (service
provided by [IBM Quantum
Experience](https://quantum-computing.ibm.com/)).

<div align="center" style="align:center; padding:20px;">
    <table style="text-align:center;">
        <thead>
            <tr>
            <th>Documentation</th>
            <th>Website</th>
            <th>Repository</th>
            </tr>
        </thead>
        <tbody>
            <tr>
            <td><a href="http://docs.quantum-robot.org/en/latest/">Link 🔗</a></td>
            <td><a href="http://quantum-robot.org">Link 🔗</a></td>
            <td><a href="https://github.com/Davidelanz/quantum-robot/">Link 🔗</a></td>
            </tr>
        </tbody>
    </table>
</div>


The project was started in 2019 by
[Davide Lanza](https://scholar.google.com/citations?user=Lqx6VqEAAAAJ)
as a Master thesis
research, with the help of
[Fulvio Mastrogiovanni](https://scholar.google.it/citations?user=9dRRzV0AAAAJ&hl=en)
and
[Paolo Solinas](https://rubrica.unige.it/personale/UkNHWllv).
It is currently maintained by [Davide Lanza](https://scholar.google.com/citations?user=Lqx6VqEAAAAJ).


## Getting Started

Check the
[Getting Started](http://docs.quantum-robot.org/en/latest/getting_started/getting_started.html)
section of the Documentation for the Installation Guide.

Demo [Notebooks](http://docs.quantum-robot.org/en/latest/notebooks/notebooks.html) 
and [Documentation](http://docs.quantum-robot.org/en/latest/documentation/documentation.html)
is made available as well

## Contributing

If you are interested in the project, we welcome new contributors of all
experience levels. For any questions, [contact the
maintainer](mailto:info@davidelanza.it).

An example module with the docstring standard we adopted is available
[here](https://github.com/Davidelanz/quantum-robot/blob/master/docs/docstring_example/template.py).

## Citing

If you use quantum-robot in a scientific publication, we would
appreciate citations to the following paper:

```{.sourceCode .bibtex}
@InProceedings{10.1007/978-3-030-71151-1_44,
    author="Lanza, Davide
        and Solinas, Paolo
        and Mastrogiovanni, Fulvio",
    editor="Siciliano, Bruno
        and Laschi, Cecilia
        and Khatib, Oussama",
    title="Multi-sensory Integration in a Quantum-Like Robot Perception Model",
    booktitle="Experimental Robotics",
    year="2021",
    publisher="Springer International Publishing",
    address="Cham",
    pages="502--509",
    isbn="978-3-030-71151-1"
}
```

## License

[GNU-GPLv3](https://github.com/Davidelanz/quantum-robot/blob/master/LICENSE)
