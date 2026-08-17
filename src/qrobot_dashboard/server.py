"""
Dashboard webapp Dash server callbacks.
"""

from collections.abc import Callable, Mapping

import dash
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State

from qrobot_qunits.redis_utils import redis_status
from qrobot_visualization import draw, graph


def build_network_figure(status: Mapping[str, str]) -> go.Figure | None:
    """Build the dashboard figure from a Redis status mapping."""
    network = graph(status)
    return draw(network, show=False, return_figure=True)


def register_callbacks(
    dash_app: dash.Dash,
    status_provider: Callable[[], Mapping[str, str]] = redis_status,
) -> dash.Dash:
    """Register server callback functions to the Dash app."""

    @dash_app.callback(
        Output("network-graph", "figure"), [Input("refresh-interval", "n_intervals")]
    )
    def _update_network_graph(_):
        return build_network_figure(status_provider())

    @dash_app.callback(
        Output("refresh-interval", "interval"), [Input("refresh-slider", "value")]
    )
    def _update_interval_rate(refresh_value):
        return refresh_value * 1000  # seconds to milliseconds

    @dash_app.callback(
        [Output("refresh-slider-text", "children")],
        [Input("refresh-interval", "n_intervals")],
        [State("refresh-slider", "value")],
    )
    def _update_refresh_interval(_, refresh_value):
        return [f"Refresh: {refresh_value*1000}ms"]

    return dash_app
