"""Dashboard web application callbacks."""

from collections.abc import Callable, Mapping

import dash
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State

from qrobot_qunits.redis_utils import redis_status
from qrobot_visualization import build_network, draw


def build_network_figure(status: Mapping[str, str]) -> go.Figure:
    """Build the dashboard figure from a Redis status mapping.

    Parameters
    ----------
    status : collections.abc.Mapping[str, str]
        Decoded qUnit Redis status.

    Returns
    -------
    plotly.graph_objects.Figure
        Rendered qUnit network figure.
    """
    network = build_network(status)
    return draw(network)


def register_callbacks(
    dash_app: dash.Dash,
    status_provider: Callable[[], Mapping[str, str]] = redis_status,
) -> dash.Dash:
    """Register server callback functions with a Dash application.

    Parameters
    ----------
    dash_app : dash.Dash
        Application that owns the callbacks.
    status_provider : collections.abc.Callable
        Zero-argument function returning decoded qUnit status.

    Returns
    -------
    dash.Dash
        The same application after callback registration.
    """

    @dash_app.callback(
        Output("network-graph", "figure"), [Input("refresh-interval", "n_intervals")]
    )
    def _update_network_graph(_: int) -> go.Figure:
        return build_network_figure(status_provider())

    @dash_app.callback(Output("refresh-interval", "interval"), [Input("refresh-slider", "value")])
    def _update_interval_rate(refresh_value: float) -> float:
        return refresh_value * 1000  # seconds to milliseconds

    @dash_app.callback(
        [Output("refresh-slider-text", "children")],
        [Input("refresh-interval", "n_intervals")],
        [State("refresh-slider", "value")],
    )
    def _update_refresh_interval(_: int, refresh_value: float) -> list[str]:
        return [f"Refresh: {refresh_value * 1000}ms"]

    return dash_app
