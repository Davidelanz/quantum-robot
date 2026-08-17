"""Tests for dashboard application construction and rendering helpers."""

from qrobot_dashboard.app import create_app
from qrobot_dashboard.server import build_network_figure


def test_create_app_builds_dashboard_server() -> None:
    """The optional dashboard package builds without contacting Redis."""
    server = create_app()

    assert server.config["DASH_TITLE"] == "Quantum-robot Dashboard"
    assert any(rule.rule == "/" for rule in server.url_map.iter_rules())


def test_build_network_figure_accepts_partial_status() -> None:
    """The dashboard can render before every qUnit has emitted an output."""
    figure = build_network_figure({"sensor class": "SensorialUnit"})

    assert figure is not None
    assert len(figure.data) == 1
