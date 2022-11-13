QUnits
=========================================

``qrobot.qunits`` module class diagram:

.. inheritance-diagram:: qrobot.qunits.SensorialUnit, qrobot.qunits.QUnit
   :top-classes: qrobot.qunits.base.BaseUnit
   :parts: 1

|

The ``BaseUnit`` abstract class
-------------------------------------

.. autoclass:: qrobot.qunits.base.BaseUnit
    :members:

|

``BaseUnit`` Globals
-------------------------------------

.. automodule:: qrobot.qunits.base
    :members: MIN_TS

|

The ``QUnit`` class
-------------------------------------

.. autoclass:: qrobot.qunits.QUnit
    :members:

|

The ``SensorialUnit`` class
-------------------------------------

.. autoclass:: qrobot.qunits.SensorialUnit
    :members:

|


Redis utilities
-------------------------------------

The module ``qrobot.qunits.redis_utils`` contains useful functions
to connect and to manage the redis database.

.. automodule:: qrobot.qunits.redis_utils
    :members: get_redis
    :noindex:

.. automodule:: qrobot.qunits.redis_utils
    :members: redis_status, flush_redis

|