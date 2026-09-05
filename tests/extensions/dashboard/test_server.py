"""Tests for dashboard graph construction and callbacks."""

from dash import Dash, html

from qrobot_dashboard.server import (
    build_network_figure,
    ordered_network,
    refresh_interval_ms,
    refresh_label,
    register_callbacks,
)


def sample_status() -> dict[str, str]:
    """Return a small live network in deliberately unstable key order."""
    return {
        "processor in_qunits": '{"0": "sensor"}',
        "sensor output": "0.6666666666666666",
        "processor class": "QUnit",
        "sensor class": "SensorialUnit",
    }


def test_ordered_network_is_stable_across_status_order() -> None:
    """Redis scan order cannot move nodes between dashboard refreshes."""
    status = sample_status()
    first = ordered_network(status)
    second = ordered_network(dict(reversed(list(status.items()))))
    assert list(first.nodes) == list(second.nodes) == ["processor", "sensor"]
    assert list(first.edges) == list(second.edges) == [("sensor", "processor")]


def test_build_network_figure_accepts_partial_status() -> None:
    """The dashboard renders before every qUnit has published an output."""
    figure = build_network_figure({"sensor class": "SensorialUnit"})
    assert [trace.mode for trace in figure.data] == ["markers", "text"]
    assert list(figure.data[0].x) == [0.0]
    assert list(figure.data[1].text) == ["<b>sensor</b>"]


def test_build_network_figure_has_stable_layout_and_compact_values() -> None:
    """Live graph updates retain positions and use readable values."""
    first = build_network_figure(sample_status())
    updated = dict(reversed(list(sample_status().items())))
    updated["sensor output"] = "1.0"
    second = build_network_figure(updated)
    assert list(first.data[-2].x) == list(second.data[-2].x)
    assert list(first.data[-2].y) == list(second.data[-2].y)
    assert first.layout.uirevision == second.layout.uirevision
    assert first.data[0].line.width < second.data[0].line.width


def test_refresh_helpers_use_dash_milliseconds() -> None:
    """Slider seconds are consistently converted for the interval and label."""
    assert refresh_interval_ms(0.5) == 500
    assert refresh_interval_ms(1.5) == 1500
    assert refresh_label(0.5) == "Refresh every 0.5 seconds"
    assert refresh_label(1) == "Refresh every 1 second"
    assert refresh_label(1.5) == "Refresh every 1.5 seconds"


def test_register_callbacks_registers_all_dashboard_updates() -> None:
    """Callback registration adds graph, interval, and label updates."""
    dash_app = Dash(__name__)
    dash_app.layout = html.Div()
    result = register_callbacks(dash_app, status_provider=sample_status)
    assert result is dash_app
    assert len(dash_app.callback_map) == 3

    graph_callback = dash_app.callback_map["network-graph.figure"]["callback"].__wrapped__
    interval_callback = dash_app.callback_map["refresh-interval.interval"]["callback"].__wrapped__
    label_callback = dash_app.callback_map["refresh-slider-text.children"]["callback"].__wrapped__
    assert graph_callback(0).layout.uirevision
    assert interval_callback(1.5) == 1500
    assert label_callback(1.5) == "Refresh every 1.5 seconds"
