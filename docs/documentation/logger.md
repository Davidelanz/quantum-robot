# Logging

quantum-robot uses standard-library loggers under the `qrobot` namespace and
never configures handlers implicitly. Applications can use
`configure_logging()` to opt into a console and/or file-based debug setup.

```python
from pathlib import Path

from qrobot.logger import LoggingConfig, configure_logging

configure_logging(LoggingConfig(level=10, file_path=Path("qrobot-debug.log"), console=True))
```

```{eval-rst}
.. automodule:: qrobot.logger
   :members: LoggingConfig, configure_logging, get_logger
```
