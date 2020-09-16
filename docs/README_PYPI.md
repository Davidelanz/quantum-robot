<div align="center" style="align:center; padding:20px">
   <a href="http://quantum-robot.org">
      <img width="300" src="https://raw.githubusercontent.com/Davidelanz/quantum-robot/master/docs/quantum-robot-logo.svg">
   </a>
</div>

<div align="center" style="align:center; padding:20px">
   <a href="https://travis-ci.com/github/Davidelanz/quantum-robot">
      <img src="https://travis-ci.com/Davidelanz/quantum-robot.svg?branch=master" alt="Build"/>
   </a>
   <a href="https://frontend.code-inspector.com/public/project/13599/quantum-robot/dashboard">
      <img src="https://www.code-inspector.com/project/13599/score/svg" alt="Code Quality"/>
   </a>
   <a href="https://codecov.io/gh/Davidelanz/quantum-robot" >
      <img src="https://codecov.io/gh/Davidelanz/quantum-robot/branch/master/graph/badge.svg?token=69IQEINMQU" alt="Code coverage"/>
   </a>
   <!--a href="https://codeclimate.com/github/Davidelanz/quantum-robot/maintainability">
      <img src="https://api.codeclimate.com/v1/badges/498a54bb981af54decec/maintainability" alt="Maintainability"/>
   </a-->
   <a>
      <img src="https://img.shields.io/badge/python-3.6|3.7|3.8-blue" alt="Python"/>
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
<!-- table align="center" style="width:70%; border: 1px solid black; margin-bottom:20px">
    <tr>
    <th> <b>BEWARE:</b> package still under developement. If you are not one of the developers, it is not suggested to install it yet.
    </tr>
</table -->

`quantum-robot` is a Python package for quantum-like perception modeling
for robotics. The package exploits [Qiksit](https://qiskit.org/)
framework, implementing the models on quantum circuits which can be
simulated on a classical computer or sent to a quantum backend (service
provided by [IBM Quantum
Experience](https://quantum-computing.ibm.com/)).

The project was started in 2019 by Davide Lanza as a Master thesis
research, with the help of [Fulvio
Mastrogiovanni](https://www.dibris.unige.it/mastrogiovanni-fulvio) and
[Paolo
Solinas](http://www.spin.cnr.it/index.php/people/46-researchers/49-solinas-paolo.html).

It is currently maintained by Davide Lanza.

-   Website: <http://quantum-robot.org>
-   Repository: <https://github.com/Davidelanz/quantum-robot/>
-   Documentation: <http://quantum-robot.org/docs>

Contents
========

-   [Install](#install)
-   [Notebooks](#notebooks)
-   [Contributing](#contributing)
-   [Citing](#citing)
-   [License](#license)

Install[↑](#contents)
=====================

Dependencies
------------

Check the required packages
[here](https://github.com/Davidelanz/quantum-robot/blob/master/requirements.txt).

User installation
-----------------

The easiest way to install *quantum-robot* is using `pip`:

    pip install -U quantum-robot

The package can be [installed from
source](https://packaging.python.org/tutorials/installing-packages/#id19)
as well. You can check the latest sources with the command:

    git clone https://github.com/Davidelanz/quantum-robot.git

Testing
-------

After installation, you can launch the test suite from outside the
source directory (you will need to have `pytest` installed):

    pytest qrobot

See also the [Getting
Started](http://www.quantum-robot.org/docs/getting_started.html) guide.

Notebooks[↑](#contents)
=======================

Several notebooks are availabe, to get started with the package and its
capabilities:

-   [One-dimensional demo for the
    AngularModel](https://github.com/Davidelanz/quantum-robot/blob/master/notebooks/demo_angular_dim1.ipynb).
-   [Three-dimensional demo for the
    AngularModel](https://github.com/Davidelanz/quantum-robot/blob/master/notebooks/demo_angular_dim3_RGB.ipynb).
-   [Computation speed analysis for the
    AngularModel](https://github.com/Davidelanz/quantum-robot/blob/master/notebooks/computation_speed.ipynb).
-   [One-dimensional comparison between AngularModel and
    LinearModel](https://github.com/Davidelanz/quantum-robot/blob/master/notebooks/model_comparison.ipynb).

Contributing [↑](#contents)
===========================

If you are interested in the project, we welcome new contributors of all
experience levels. For any question, [contact the
maintainer](mailto:davidel96@hotmail.it).

An example module with the docstring standard we adopted is available
[here](https://github.com/Davidelanz/quantum-robot/blob/master/docs/example/qrobot_doc.py).

::: {.note}
::: {.admonition-title}
Note
:::

The documentation build workflow is the following one:

1.  Modify the `.rst` modules in the `docs/modules` folder of the Github
    repository, or the high-level `.rst` modules in the `docs` folder
    (`getting_started.rst`, `index.rst`, `models.rst`)
2.  Build the `README.rst` file with the `readme_export.py` Python 3
    script in the `docs` folder
3.  Build the `README_PYPI.md` file with the `readme_pypi_export.sh`
    bash script
4.  Run the `make html` Sphinx command to build the documentation HTML
    files
:::

Citing [↑](#contents)
=====================

If you use quantum-robot in a scientific publication, we would
appreciate citations to the following paper:

``` {.sourceCode .bibtex}
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

License [↑](#contents)
======================

[GNU-GPLv3](https://github.com/Davidelanz/quantum-robot/blob/master/LICENSE)
