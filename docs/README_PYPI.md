<div style=" display: block; margin-left: auto; margin-right: auto; width: 400px;">
   <img src="https://raw.githubusercontent.com/Davidelanz/quantum-robot/master/docs/quantum-robot-logo.svg">
</div>

[![Build](https://travis-ci.com/Davidelanz/quantum-robot.svg?token=BnWGyPSEGJoK3Kmq8jGJ&branch=massvg)](https://travis-ci.com/github/Davidelanz/quantum-robot)

[![Code coverage](https://codecov.io/gh/Davidelanz/quantum-robot/branch/master/graph/badge.svg?token=69IQEINMQU)](https://codecov.io/gh/Davidelanz/quantum-robot)

[![Maintainability](https://api.codeclimate.com/v1/badges/498a54bb981af54decec/maintainability)](https://codeclimate.com/github/Davidelanz/quantum-robot/maintainability)

[![Development Status](https://pypip.in/status/quantum-robot/badge.svg)](https://pypi.org/project/quantum-robot/)

[![Python](https://img.shields.io/badge/python-3.6%7C3.7%7C3.8-blue)](#)

[![PyPi version](https://badge.fury.io/py/quantum-robot.svg)](https://pypi.org/project/quantum-robot/)

[![License](https://img.shields.io/badge/license-GNU_GPL_v3-blue)](https://github.com/Davidelanz/quantum-robot/blob/master/LICENSE)

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

See the required packages
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

Citing [↑](#contents)
=====================

If you use quantum-robot in a scientific publication, we would
appreciate citations to the following paper:

``` {.sourceCode .bibtex}
@misc{lanza2020preliminary,
    title={A Preliminary Study for a Quantum-like Robot Perception Model},
    author={Davide Lanza and Paolo Solinas and Fulvio Mastrogiovanni},
    year={2020},
    eprint={2006.02771},
    archivePrefix={arXiv},
    primaryClass={cs.RO},
    note={preprint at \url{https://arxiv.org/abs/2006.02771}},
}
```

License [↑](#contents)
======================

[GNU-GPLv3](https://github.com/Davidelanz/quantum-robot/blob/master/LICENSE)
