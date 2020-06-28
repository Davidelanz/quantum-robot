[![Build](https://travis-ci.com/Davidelanz/quantum-robot.svg?token=BnWGyPSEGJoK3Kmq8jGJ&branch=master)](https://travis-ci.com/github/Davidelanz/quantum-robot)

[![Code coverage](https://codecov.io/gh/Davidelanz/quantum-robot/branch/master/graph/badge.svg?token=69IQEINMQU)](https://codecov.io/gh/Davidelanz/quantum-robot)

[![Maintainability](https://api.codeclimate.com/v1/badges/498a54bb981af54decec/maintainability)](https://codeclimate.com/github/Davidelanz/quantum-robot/maintainability)

[![Development Status](https://pypip.in/status/quantum-robot/badge.svg)](https://pypi.org/project/quantum-robot/)

[![Linux](https://img.shields.io/badge/linux-xenial%7Cbionic-blue)](#)

[![Python](https://img.shields.io/badge/python-3.6%7C3.7%7C3.8-blue)](#)

[![PyPi version](https://badge.fury.io/py/quantum-robot.svg)](https://pypi.org/project/quantum-robot/)

[![License](https://img.shields.io/badge/license-GNU_GPL-blue)](https://github.com/Davidelanz/quantum-robot/blob/master/LICENSE)

<table align="center" style="width:70%; border: 1px solid black; margin-bottom:20px">
    <tr>
    <th> <b>BEWARE:</b> package still under developement. If you are not one of the developers, it is not suggested to install it yet.
    </tr>
</table>

`quantum-robot` is a Python package for quantum-like perception modeling
for robotics. The package exploits [Qiksit](https://qiskit.org/)
framework, implementing the models on quantum circuits which can be
simulated on a classical computer or sent to a quantum backend (service
provided by [IBM Quantum
Experience](https://quantum-computing.ibm.com/)). A
[ROS](https://www.ros.org/) implementation is provided, in order to
easily adapt the framework for real-time applications in robotics.

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
-   [Notebooks](#license)
-   [License](#license)

Install[↑](#contents)
=====================

Dependencies
------------

See the
[requirements](https://github.com/Davidelanz/quantum-robot/blob/master/requirements.txt)

User installation
-----------------

The easiest way to install `quantum-robot` is using `pip`:

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

Computation speed tests
[available](https://github.com/Davidelanz/quantum-robot/blob/master/notebooks/computation_speed.ipynb).

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

License[↑](#contents)
=====================

[GNU
GPL](https://github.com/Davidelanz/quantum-robot/blob/master/LICENSE)
