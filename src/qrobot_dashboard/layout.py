"""Declarative components that make up the dashboard page."""

from dash import dcc, html
from dash.development.base_component import Component

DEFAULT_REFRESH_SECONDS = 1.0
MIN_REFRESH_SECONDS = 0.5
MAX_REFRESH_SECONDS = 10.0
REFRESH_MARKS = {0.5: "0.5", 1: "1", 2: "2", 5: "5", 10: "10 s"}
REFRESH_SLIDER_ID = "refresh-slider"
REFRESH_LABEL_ID = "refresh-slider-text"
REFRESH_INTERVAL_ID = "refresh-interval"
NETWORK_GRAPH_ID = "network-graph"


def build_controls() -> Component:
    """Build the dashboard heading and refresh controls.

    Returns
    -------
    dash.development.base_component.Component
        Container holding the title, slider, and current refresh label.
    """
    return html.Div(
        className="container width60",
        children=[
            html.H1("Quantum-robot Dashboard"),
            html.Div(
                className="row",
                children=[
                    dcc.Slider(
                        id=REFRESH_SLIDER_ID,
                        min=MIN_REFRESH_SECONDS,
                        max=MAX_REFRESH_SECONDS,
                        step=0.5,
                        value=DEFAULT_REFRESH_SECONDS,
                        marks=REFRESH_MARKS,
                        updatemode="mouseup",
                    ),
                    html.Div(id=REFRESH_LABEL_ID),
                ],
            ),
        ],
    )


def build_network_panel() -> Component:
    """Build the live qBrain network panel.

    Returns
    -------
    dash.development.base_component.Component
        Container holding the graph description and Plotly graph.
    """
    return html.Div(
        className="container width90",
        children=[
            html.H2("Network Graph"),
            html.P(
                "Thicker connections indicate stronger signals (0-1). "
                "Hover over a node for its exact output.",
                style={"fontSize": "13px"},
            ),
            html.Div(
                className="row",
                children=[dcc.Graph(className="graph", id=NETWORK_GRAPH_ID)],
            ),
        ],
    )


def build_layout() -> Component:
    """Build a new root component for the dashboard.

    Returns
    -------
    dash.development.base_component.Component
        Complete dashboard page layout.
    """
    return html.Div(
        children=[
            build_controls(),
            build_network_panel(),
            dcc.Interval(
                id=REFRESH_INTERVAL_ID,
                interval=int(DEFAULT_REFRESH_SECONDS * 1000),
                n_intervals=0,
            ),
        ]
    )


layout = build_layout()
