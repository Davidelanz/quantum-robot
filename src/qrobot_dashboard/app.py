"""Application factory for the Redis-backed qUnit dashboard."""

from dash import Dash
from flask import Flask

from qrobot_dashboard.layout import build_layout
from qrobot_dashboard.server import register_callbacks

VIEWPORT_META = {
    "name": "viewport",
    "content": "width=device-width, initial-scale=1, shrink-to-fit=no",
}


def create_dash_app(server: Flask) -> Dash:
    """Create and configure the Dash application mounted on a Flask server.

    Parameters
    ----------
    server : flask.Flask
        Configured Flask server that will host the dashboard.

    Returns
    -------
    dash.Dash
        Dashboard application with its layout and callbacks registered.
    """
    dash_app = Dash(
        __name__,
        server=server,  # type: ignore[arg-type]  # Dash's stub omits Flask apps.
        url_base_pathname="/",
        assets_folder=server.config["DASH_ASSETS_DIR"],
        meta_tags=[VIEWPORT_META],
    )
    dash_app.title = server.config["DASH_TITLE"]
    dash_app.layout = build_layout
    dash_app.css.config.serve_locally = True
    dash_app.enable_dev_tools(
        debug=server.config["DASH_DEBUG"],
        dev_tools_hot_reload=server.config["DASH_AUTORELOAD"],
    )
    return register_callbacks(dash_app)


def create_app(config_object_name: str = "qrobot_dashboard.config.Config") -> Flask:
    """Create the Flask server and mount the qUnit dashboard on it.

    Parameters
    ----------
    config_object_name : str
        Import path of the Flask configuration object.

    Returns
    -------
    flask.Flask
        Configured Flask server containing the Dash application.

    Notes
    -----
    Run the app via ``FLASK_APP=qrobot_dashboard.app:create_app flask run``.
    """
    server = Flask(__name__)
    server.config.from_object(config_object_name)
    with server.app_context():
        create_dash_app(server)

    return server
