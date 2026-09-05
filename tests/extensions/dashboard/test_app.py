"""Tests for the dashboard application factory."""

from flask import Flask

from qrobot_dashboard.app import VIEWPORT_META, create_app, create_dash_app
from qrobot_dashboard.config import Config


def test_create_dash_app_mounts_layout_and_callbacks() -> None:
    """The Dash application is fully configured on its Flask server."""
    server = Flask(__name__)
    server.config.from_object(Config)

    dash_app = create_dash_app(server)

    assert dash_app.title == Config.DASH_TITLE
    assert callable(dash_app.layout)
    assert dash_app.config.meta_tags == [VIEWPORT_META]
    assert len(dash_app.callback_map) == 3


def test_create_app_builds_dashboard_server() -> None:
    """The public factory mounts the dashboard without contacting Redis."""
    server = create_app()

    assert server.config["DASH_TITLE"] == Config.DASH_TITLE
    assert any(rule.rule == "/" for rule in server.url_map.iter_rules())
