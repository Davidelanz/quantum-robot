"""
Dashboard webapp Dash server callbacks.
"""
import dash
from dash.dependencies import Input, Output, State

from qrobot.draw.draw import draw
from qrobot.graph.graph import graph
from qrobot.qunits.redis_utils import redis_status


def register_callbacks(dash_app: dash.Dash) -> dash.Dash:
    """Register server callback functions to the Dash app."""

    @dash_app.callback(
        Output("network-graph", "figure"), [Input("refresh-interval", "n_intervals")]
    )
    def _update_network_graph(_):
        status = redis_status()
        network = graph(status)
        figure = draw(network, show=False, return_figure=True)
        return figure

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
