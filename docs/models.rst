Models
=========================================


The ``Model`` abstract class
----------------------------

This class is the parent class which defines the general features a perception model has to implement. 
It is used to define custom models as a child classes::
    from qrobot.models import Model

    class myModel(Model):
        (...)

.. autoclass:: qrobot.models.Model
    :members:



The ``AngularModel`` class
--------------------------

This is a custom model provided by the package.  This model encodes the perceptual information in 
the angle of the qubits’ Bloch sphere representations.

.. autoclass:: qrobot.models.AngularModel
    :members:

