
.. image:: https://travis-ci.com/Davidelanz/quantum-robot.svg?token=BnWGyPSEGJoK3Kmq8jGJ&branch=master
   :target: https://travis-ci.com/github/Davidelanz/quantum-robot
   :alt: Build
.. image:: https://codecov.io/gh/Davidelanz/quantum-robot/branch/master/graph/badge.svg?token=69IQEINMQU
   :target: https://codecov.io/gh/Davidelanz/quantum-robot
   :alt: Code coverage
.. image:: https://api.codeclimate.com/v1/badges/498a54bb981af54decec/maintainability
   :target: https://codeclimate.com/github/Davidelanz/quantum-robot/maintainability
   :alt: Maintainability
.. image:: https://pypip.in/status/quantum-robot/badge.svg
   :target: https://pypi.org/project/quantum-robot/
   :alt: Development Status
.. image:: https://img.shields.io/badge/python-3.6|3.7|3.8-blue
   :target: #
   :alt: Python
.. image:: https://badge.fury.io/py/quantum-robot.svg
   :target: https://pypi.org/project/quantum-robot/
   :alt: PyPi version
.. image:: https://img.shields.io/badge/license-GNU_GPL_v3-blue
   :target: https://github.com/Davidelanz/quantum-robot/blob/master/LICENSE 
   :alt: License


.. raw:: html

   <!-- table align="center" style="width:70%; border: 1px solid black; margin-bottom:20px">
       <tr>
       <th> <b>BEWARE:</b> package still under developement. If you are not one of the developers, it is not suggested to install it yet.
       </tr>
   </table -->


``quantum-robot`` is a Python package for quantum-like perception modeling for robotics. 
The package exploits `Qiksit <https://qiskit.org/>`__ framework, implementing the models on
quantum circuits which can be simulated on a classical computer or sent to a quantum 
backend (service provided by `IBM Quantum Experience <https://quantum-computing.ibm.com/>`__).

The project was started in 2019 by Davide Lanza as a Master thesis research, with the help
of `Fulvio Mastrogiovanni <https://www.dibris.unige.it/mastrogiovanni-fulvio>`__ and `Paolo
Solinas <http://www.spin.cnr.it/index.php/people/46-researchers/49-solinas-paolo.html>`__.

It is currently maintained by Davide Lanza.

- Website: http://quantum-robot.org
- Repository: https://github.com/Davidelanz/quantum-robot/
- Documentation: http://quantum-robot.org/docs

 
Contents
--------

-  `Install <#install>`__
-  `Notebooks <#notebooks>`__
-  `Contributing <#contributing>`__
-  `Citing <#citing>`__
-  `License <#license>`__


Install\ `↑ <#contents>`__
-----------------------------------------
Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~


See the required packages `here <https://github.com/Davidelanz/quantum-robot/blob/master/requirements.txt>`_.


User installation
~~~~~~~~~~~~~~~~~~~~~~~~

The easiest way to install *quantum-robot* is using ``pip``::

    pip install -U quantum-robot


The package can be `installed from
source <https://packaging.python.org/tutorials/installing-packages/#id19>`__
as well. You can check the latest sources with the command::

    git clone https://github.com/Davidelanz/quantum-robot.git



Testing
~~~~~~~~~~~~~~~~~~~~~~~~

After installation, you can launch the test suite from outside the
source directory (you will need to have ``pytest`` installed):

::

    pytest qrobot

 
See also the `Getting Started <http://www.quantum-robot.org/docs/getting_started.html>`__
guide.


Notebooks\ `↑ <#contents>`__
---------------------------------------


Several notebooks are availabe, to get started with the package and its capabilities:

- `One-dimensional demo for the AngularModel <https://github.com/Davidelanz/quantum-robot/blob/master/notebooks/demo_angular_dim1.ipynb>`__.
- `Three-dimensional demo for the AngularModel <https://github.com/Davidelanz/quantum-robot/blob/master/notebooks/demo_angular_dim3_RGB.ipynb>`__.
- `Computation speed analysis for the AngularModel <https://github.com/Davidelanz/quantum-robot/blob/master/notebooks/computation_speed.ipynb>`__.
- `One-dimensional comparison between AngularModel and LinearModel <https://github.com/Davidelanz/quantum-robot/blob/master/notebooks/model_comparison.ipynb>`__.

 
Contributing `↑ <#contents>`__
---------------------------------------


If you are interested in the project, we welcome new contributors 
of all experience levels. 
For any question, `contact the maintainer <mailto:davidel96@hotmail.it>`_.

An example module with the docstring standard we adopted is available 
`here <https://github.com/Davidelanz/quantum-robot/blob/master/docs/example/qrobot_doc.py>`_.
 
Citing `↑ <#contents>`__
---------------------------------------


If you use quantum-robot in a scientific publication, we would appreciate citations to the following paper:

.. code-block:: bibtex

    @misc{lanza2020preliminary,
        title={A Preliminary Study for a Quantum-like Robot Perception Model},
        author={Davide Lanza and Paolo Solinas and Fulvio Mastrogiovanni},
        year={2020},
        eprint={2006.02771},
        archivePrefix={arXiv},
        primaryClass={cs.RO},
        note={preprint at \url{https://arxiv.org/abs/2006.02771}},
    }

 
License `↑ <#contents>`__
---------------------------------------


`GNU-GPLv3 <https://github.com/Davidelanz/quantum-robot/blob/master/LICENSE>`__
 