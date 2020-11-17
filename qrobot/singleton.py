""" 
Thread-safe Singleton implementation from 
https://stackoverflow.com/questions/50566934/why-is-this-singleton-implementation-not-thread-safe

''The metaclass-based implementation is the most frequently used. 
  As for for thread-safety (...) it is always possible that a thread reads that 
  there is no existing instance and starts creating one, but another thread does 
  the same before the first instance was stored.
  You can use a with lock controller to protect the __call__ method of a 
  metaclass-based singleton class with a lock.''
"""

import threading

lock = threading.Lock()


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with lock:
                if cls not in cls._instances:
                    cls._instances[cls] = \
                        super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SingletonClass(metaclass=Singleton):
    pass
