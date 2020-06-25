quantum-robot
=============

.. raw:: html

   <p>    <!--align="center" -->
       <a href="https://travis-ci.com/github/Davidelanz/quantum-robot" alt="Build">
           <img src="https://travis-ci.com/Davidelanz/quantum-robot.svg?token=BnWGyPSEGJoK3Kmq8jGJ&branch=master" />
       </a>
       <a href="https://codecov.io/gh/Davidelanz/quantum-robot" alt="Code coverage">
           <img src="https://codecov.io/gh/Davidelanz/quantum-robot/branch/master/graph/badge.svg?token=69IQEINMQU" />
       </a>
       <a href="https://lgtm.com/projects/g/Davidelanz/quantum-robot/context:python">
           <img alt="Language grade: Python" src="https://img.shields.io/lgtm/grade/python/g/Davidelanz/quantum-robot.svg?logo=lgtm&logoWidth=18"/>
       </a>
       <a href="#" alt="Development Status">
           <img src="https://pypip.in/status/quantum-robot/badge.svg" />
       </a>
       <a href="#" alt="Linux">
           <img src="https://img.shields.io/badge/linux-xenial | bionic-blue" />
       </a>
       <a href="#" alt="Python">
           <img src="https://img.shields.io/badge/python-3.6 | 3.7 | 3.8 -blue" />
       </a>
       <a href="https://pypi.org/project/quantum-robot/" alt="PyPi version">
           <img src="https://badge.fury.io/py/quantum-robot.svg" />
       </a>
       <a href="https://github.com/Davidelanz/quantum-robot/blob/master/LICENSE" alt="License">
           <img src="https://img.shields.io/badge/license-GNU GPL-blue" />
       </a>
   </p>

.. raw:: html

   <table align="center" style="width:80%; border: 1px solid black;">
       <tr>
       <th> <b>BEWARE:</b> package still under developement. If you are not one of the developers, it is not suggested to install it yet.
       </tr>
   </table>

.. raw:: html

   </p>

``quantum-robot`` is a Python package for quantum-like perception modeling for robotics. 
The package exploits `Qiksit <https://qiskit.org/>`__ framework, implementing the models on
quantum circuits which can be simulated on a classical computer or sent to a quantum 
backend (service provided by `IBM Quantum Experience <https://quantum-computing.ibm.com/>`__).
A `ROS <https://www.ros.org/>`__ implementation is provided, in order to easily adapt the
framework for real-time applications in robotics.

The project was started in 2019 by Davide Lanza as a Master thesis research, with the help
of `Fulvio Mastrogiovanni <https://www.dibris.unige.it/mastrogiovanni-fulvio>`__ and `Paolo
Solinas <http://www.spin.cnr.it/index.php/people/46-researchers/49-solinas-paolo.html>`__.

It is currently maintained by Davide Lanza.

Website: http://quantum-robot.org Contents
--------

-  `Install <#install>`__
-  `License <#license>`__

Install\ `↑ <#summary>`__
------------------------------
Dependencies
~~~~~~~~~~~~

See the `requirements <https://github.com/Davidelanz/quantum-robot/blob/master/requirements.txt>`__

User installation
~~~~~~~~~~~~~~~~~

The easiest way to install ``quantum-robot`` is using ``pip``:

::

    pip install -U quantum-robot

The package can be `installed from
source <https://packaging.python.org/tutorials/installing-packages/#id19>`__
as well. You can check the latest sources with the command:

::

    git clone https://github.com/Davidelanz/quantum-robot.git

Testing
~~~~~~~

After installation, you can launch the test suite from outside the
source directory (you will need to have ``pytest`` installed):

::

    pytest qrobot

Computation speed tests
`available <https://github.com/Davidelanz/quantum-robot/blob/master/notebooks/computation_speed.ipynb>`__. License\ `↑ <#summary>`__
-------------------------

`GNU
GPL <https://github.com/Davidelanz/quantum-robot/blob/master/LICENSE>`__

