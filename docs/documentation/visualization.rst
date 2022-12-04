Visualization
=========================================


Graph
-------------------------------------

The ``quantum-robot`` unit processes communicate in between each other
via Redis entries. With the ``qrobot.graph`` function it is possible
to generate a ``networkx`` directed graph containing all the running
units as connected nodes.


.. automodule:: qrobot
   :members: graph
   :noindex:



Draw
-------------------------------------


With the ``qrobot.graph`` function it is possible to generate a ``networkx`` directed graph containing all the running units as connected nodes.
The ``qrobot.draw`` function allows to visualize such graph.


.. automodule:: qrobot
   :members: draw
   :noindex:



Dashboard
-------------------------------------

.. warning::
    The Dashboard is still on development and should not be used
    if not for mere testing purposes.

.. automodule:: qrobot.dashboard.server
    :members:
