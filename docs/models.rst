************
Models
************

.. include:: modules/models_diagram.rst

|

The ``Model`` abstract class
=========================================

This class is the parent class which defines the general features a perception model has to implement. 
It is used to define custom models as a child classes::
    
    from qrobot.models import Model

    class myModel(Model):
        (...)

.. autoclass:: qrobot.models.Model
    :members:


|

The ``AngularModel`` class
=========================================

This is a custom ``Model`` provided by the package. This model encodes the perceptual information in 
the angle of the qubits’ Bloch sphere representations.

.. autoclass:: qrobot.models.AngularModel
    :members:


|

The ``LinearModel`` class
=========================================

This is a custom model derived from ``AngularModel``, which corrects it with a nonlinear encoding. 
By means of its nonlinear encoding, this model provides a linear decoding 
(a `notebook <https://github.com/Davidelanz/quantum-robot/blob/master/notebooks/model_comparison.ipynb>`_ 
is provided in order to illustrate the difference between this and the angular one).

.. autoclass:: qrobot.models.LinearModel
    :members:


|

The ``BurstAModel`` class
=========================================

This is a modified ``AngularModel`` which provides a burst instead of a 
dictionary as decoding, which is the ration of qubits recorded in a \|0> state 
out of the dimension of the mode:

.. code-block:: python

    >>> AngularModel.decode(model)
    {"state" = 1}
    >>> BurstAModel.decode(model)
    float

    # E.g.
    >>> AngularModel.decode(model)
    {"111100" = 1}
    >>> BurstAModel.decode(model)
    2/6 = 0.3333333333333333

.. autoclass:: qrobot.models.BurstAModel
    :members:


|

Module variables
=========================================

.. automodule:: qrobot.models.model
    :members: QASM_BACKEND