"""Dash web application for monitoring qUnits on a shared Redis server."""

import os

from dash import Dash
from flask import Flask

from qrobot_dashboard.layout import layout
from qrobot_dashboard.server import register_callbacks


def create_app(config_object_name: str = "qrobot_dashboard.config.Config") -> Flask:
    """Create the Flask server and mount the qUnit dashboard on it.

    Run the app via ``FLASK_APP=qrobot_dashboard.app:create_app flask run``."""
    server = Flask(__name__, static_folder="static")

    server.config.from_object(config_object_name)

    # Meta tags for viewport responsiveness
    meta_viewport = {
        "name": "viewport",
        "content": "width=device-width, initial-scale=1, shrink-to-fit=no",
    }

    my_dash_app = Dash(
        __name__,
        server=server,  # type: ignore[arg-type]  # Dash's stub omits Flask apps.
        url_base_pathname="/",
        assets_folder=server.config["DASH_ASSETS_DIR"],
        meta_tags=[meta_viewport],
        # external_stylesheets=[],
        # external_scripts=[]
    )

    with server.app_context():
        my_dash_app.title = server.config["DASH_TITLE"]
        my_dash_app.layout = layout
        my_dash_app.css.config.serve_locally = True
        my_dash_app.enable_dev_tools(
            debug=server.config["DASH_DEBUG"],
            dev_tools_hot_reload=server.config["DASH_AUTORELOAD"],
        )
        my_dash_app = register_callbacks(my_dash_app)

    # Report the process that owns this app instance in multi-worker deployments.
    print(f"Flask With Dash Apps Built Successfully with PID {str(os.getpid())}.")

    return server
