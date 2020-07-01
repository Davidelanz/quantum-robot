<div align="center" style="align:center; padding:20px">
   <a href="http://quantum-robot.org">
      <img width="300" src="https://raw.githubusercontent.com/Davidelanz/quantum-robot/master/docs/quantum-robot-logo.svg">
   </a>
</div>
<br>
<div align="center" style="align:center; padding:20px">
   <a href="https://travis-ci.com/github/Davidelanz/quantum-robot" alt="Build">
      <img src="https://travis-ci.com/Davidelanz/quantum-robot.svg?token=BnWGyPSEGJoK3Kmq8jGJ&branch=massvg"/>
   </a>
   <a href="https://codecov.io/gh/Davidelanz/quantum-robot" alt="Code coverage">
      <img src="https://codecov.io/gh/Davidelanz/quantum-robot/branch/master/graph/badge.svg?token=69IQEINMQU"/>
   </a>
   <a href="https://codeclimate.com/github/Davidelanz/quantum-robot/maintainability" alt="Maintainability">
      <img src="https://api.codeclimate.com/v1/badges/498a54bb981af54decec/maintainability"/>
   </a>
   <a href="https://pypi.org/project/quantum-robot/" alt="Development Status">
      <img src="https://pypip.in/status/quantum-robot/badge.svg"/>
   </a>
   <a href="" alt="Python">
      <img src="https://img.shields.io/badge/python-3.6|3.7|3.8-blue"/>
   </a>
   <a href="https://pypi.org/project/quantum-robot/" alt="PyPi version">
      <img src="https://badge.fury.io/py/quantum-robot.svg"/>
   </a>
   <a href="https://github.com/Davidelanz/quantum-robot/blob/master/LICENSE" alt="License">
      <img src="https://img.shields.io/badge/license-GNU_GPL_v3-blue"/>
   </a>
</div>
<br>
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

-   Install
-   Notebooks
-   Contributing
-   Citing
-   License

Install
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


Contributing
===========================

If you are interested in the project, we welcome new contributors of all
experience levels. For any question, [contact the
maintainer](mailto:davidel96@hotmail.it).

An example module with the docstring standard we adopted is available
[here](https://github.com/Davidelanz/quantum-robot/blob/master/docs/example/qrobot_doc.py).


License
======================

[GNU-GPLv3](https://github.com/Davidelanz/quantum-robot/blob/master/LICENSE)
