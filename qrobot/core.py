
import json
import multiprocessing
import os

from flask import Flask

from .logs import get_logger
from .singleton import Singleton


class Core(object, metaclass=Singleton):
    """
    Core Flask app wrapped into a subprocess.
    Singleton implementation prevents from creating more than one instance.
    """

    def __init__(self) -> None:
        # Initialize logger
        self._logger = get_logger(__file__)
        # Initialize flask app
        self._app = self.__app_init()
        # Initialize correspondent thread
        self._process = None
        # Initialize qunits list
        self._qunits = {}


    def start(self) -> None:
        """Start the Core in a background thread"""
        if self._process is None:
            # New instance of a process
            self._process = multiprocessing.Process(target=self.__run)
        if not self._process.is_alive():
            self._logger.info(f"Starting Core process")
            self._process.start()
        else:
            # Do nothing if the Core is already running
            pass

    def stop(self) -> None:
        """Stops the Core background thread"""
        if self._process is None:
            self._logger.warning("Trying to stop Core, but it's not running")
        else:
            self._logger.info("Stopping Core process")
            self._process.terminate()
            self._process = None

    def add_qunit(self, qunit) -> None:
        self._qunits[qunit.id] = qunit

    @staticmethod
    def __app_init(test_config=None):
        # create and configure the app
        app = Flask("qrobot", instance_relative_config=True)
        app.config.from_mapping(
            SECRET_KEY='dev',
            DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        )

        if test_config is None:
            # load the instance config, if it exists, when not testing
            app.config.from_pyfile('config.py', silent=True)
        else:
            # load the test config if passed in
            app.config.from_mapping(test_config)

        # ensure the instance folder exists
        try:
            os.makedirs(app.instance_path)
        except OSError:
            pass

        return app

    def __run(self):
        # make routings
        @self._app.route('/')
        def index():
            return 'Welcome at the Quantum Robot core'

        # the root page
        @self._app.route('/qunits/')
        def qunits():
            return str(self._qunits)
        
        self._app.run()