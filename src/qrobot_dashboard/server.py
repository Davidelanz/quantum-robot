"""Dashboard web application callbacks."""

from collections.abc import Callable, Mapping

import dash
import networkx as nx
import plotly.graph_objects as go
from dash.dependencies import Input, Output

from qrobot_dashboard.figure import build_live_figure
from qrobot_dashboard.layout import (
    NETWORK_GRAPH_ID,
    REFRESH_INTERVAL_ID,
    REFRESH_LABEL_ID,
    REFRESH_SLIDER_ID,
)
from qrobot_qunits.redis.utils import redis_status
from qrobot_visualization import build_network

MILLISECONDS_PER_SECOND = 1000


def ordered_network(status: Mapping[str, str]) -> nx.DiGraph:
    """Build a network whose iteration order is stable across Redis scans.

    Parameters
    ----------
    status : collections.abc.Mapping[str, str]
        Decoded qUnit Redis status.

    Returns
    -------
    networkx.DiGraph
        Network with nodes and edges inserted in deterministic order.
    """
    source = build_network(status)
    network = nx.DiGraph()
    network.add_nodes_from(sorted(source.nodes(data=True)))
    network.add_edges_from(sorted(source.edges(data=True)))
    return network


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
    network = ordered_network(status)
    return build_live_figure(network)


def refresh_interval_ms(refresh_seconds: float) -> int:
    """Convert the refresh slider value to milliseconds.

    Parameters
    ----------
    refresh_seconds : float
        Refresh period selected by the user, in seconds.

    Returns
    -------
    int
        Refresh period expected by :class:`dash.dcc.Interval`.
    """
    return round(refresh_seconds * MILLISECONDS_PER_SECOND)


def refresh_label(refresh_seconds: float) -> str:
    """Describe the selected dashboard refresh period.

    Parameters
    ----------
    refresh_seconds : float
        Refresh period selected by the user, in seconds.

    Returns
    -------
    str
        Human-readable refresh label.
    """
    unit = "second" if refresh_seconds == 1 else "seconds"
    return f"Refresh every {refresh_seconds:g} {unit}"


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
        Output(NETWORK_GRAPH_ID, "figure"), [Input(REFRESH_INTERVAL_ID, "n_intervals")]
    )
    def _update_network_graph(_: int) -> go.Figure:
        return build_network_figure(status_provider())

    @dash_app.callback(Output(REFRESH_INTERVAL_ID, "interval"), [Input(REFRESH_SLIDER_ID, "value")])
    def _update_interval_rate(refresh_value: float) -> int:
        return refresh_interval_ms(refresh_value)

    @dash_app.callback(
        Output(REFRESH_LABEL_ID, "children"),
        [Input(REFRESH_SLIDER_ID, "value")],
    )
    def _update_refresh_interval(refresh_value: float) -> str:
        return refresh_label(refresh_value)

    return dash_app
