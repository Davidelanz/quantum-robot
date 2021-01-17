Models
=========================================

``qrobot.models`` module class diagram:

.. inheritance-diagram:: qrobot.models.Model qrobot.models.AngularModel qrobot.models.LinearModel
   :top-classes: qrobot.models.model.Model
   :parts: 1


The ``Model`` abstract class
-------------------------------------

This class is the parent class which defines the general features a perception model has to implement.
It is used to define custom models as a child classes::
   
    from qrobot.models import Model

    class myModel(Model):
        (...)

.. autoclass:: qrobot.models.Model
    :members:



The ``AngularModel`` class
-------------------------------------

This is a custom ``Model`` provided by the package. This model encodes the perceptual information in
the angle of the qubits’ Bloch sphere representations.

.. autoclass:: qrobot.models.AngularModel
    :members:



The ``LinearModel`` class
-------------------------------------

This is a custom model derived from ``AngularModel``, which corrects it with a nonlinear encoding.
By means of its nonlinear encoding, this model provides a linear decoding
(a `notebook <https://github.com/Davidelanz/quantum-robot/blob/master/notebooks/model_comparison.ipynb>`_
is provided in order to illustrate the difference between this and the angular one).

.. autoclass:: qrobot.models.LinearModel
    :members:


Module variables
-------------------------------------

.. automodule:: qrobot.models.model
    :members: QASM_BACKEND