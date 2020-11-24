
import json
import multiprocessing
import os

from flask import Flask, render_template

from ..logs import get_logger
from .singleton import Singleton

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
STATIC_DIR = os.path.join(FILE_DIR, "static")
TEMPLATES_DIR = os.path.join(FILE_DIR, "templates")

class Core(object, metaclass=Singleton):
    """
    Core Flask app wrapped into a subprocess.
    Singleton implementation prevents from creating more than one instance.
    """

    def __init__(self) -> None:
        # Initialize logger
        self._logger = get_logger("core")
        # Initialize flask app
        self._app = self.__app_init()
        # Initialize correspondent thread
        self._process = None

        # Initialize multiprocessing variables (common to all threads while
        # being modified)
        manager = multiprocessing.Manager()
        # Initialize qunits dictionary
        self._qunits = manager.dict()

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

    def remove_qunit(self, qunit) -> None:
        self._qunits.pop(qunit.id)

    @staticmethod
    def __app_init(test_config=None):
        # create and configure the app
        app = Flask("qrobot",
                    instance_relative_config=True,
                    static_url_path=TEMPLATES_DIR)
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
            return render_template('index.html', name="name")

        # the root page
        @self._app.route('/qunits/')
        def qunits():
            return str(self._qunits)

        self._app.run()
