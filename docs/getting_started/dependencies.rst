Redis database
------------------------

The quantum-robot package requires `Redis <https://redis.io>`_.
Redis is a high performance, super fast and easy to use in-memory
database.

.. figure:: https://github.com/dspezia/redis-doc/raw/client_command/topics/Data_size.png
    :width: 400
    :align: center  
    :target: https://redis.io/topics/benchmarks
    
    Check the `How fast is Redis? <https://redis.io/topics/benchmarks>`_ benchmark page for further information


**Install Redis from the official Ubuntu PPA**

You can install the latest stable version of Redis from the 
``redislabs/redis`` package repository. Add the repository 
to the ``apt`` index, update it and install:

.. code-block::

    $ sudo add-apt-repository ppa:redislabs/redis
    $ sudo apt-get update
    $ sudo apt-get install redis

**Install Redis from Snapcraft**

You can install the latest stable version of Redis from the Snapcraft 
marketplace:

.. code-block::
    
    $ sudo snap install redis

**Redis for Windows**

A port for Windows based on Redis is available at 
https://github.com/MicrosoftArchive/redis. This project though is no longer
being actively maintained. 
If you are looking for a Windows version of Redis, you may want to check out 
`Memurai <https://www.memurai.com/>`_.

**Build from source**

Check the https://redis.io/download#installation page for dedicated  
instructions and further information.

**Python package**

The `redis-py <https://github.com/andymccurdy/redis-py>`_ package 
is defined on the `Redis website <https://redis.io/clients#python>`_ as 
"the way to go for Python".

Python requirements
------------------------

Check the required packages 
`here <https://github.com/Davidelanz/quantum-robot/blob/master/requirements.txt>`_.


Docker image
------------------------

.. note::

    A Docker image will be released soon.