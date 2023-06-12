"""
Dashboard webapp Dash layout.
"""
from dash import dcc, html

layout = html.Div(
    children=[
        html.Div(
            className="container width60",
            children=[
                html.H1(children="Quantum-robot Dashboard"),
                html.Div(
                    className="row",
                    children=[
                        dcc.Slider(
                            id="refresh-slider", min=0.5, max=2, step=0.5, value=1
                        ),
                        html.Div(id="refresh-slider-text"),
                    ],
                ),
                html.H2(children="Network Graph"),
                html.Div(
                    className="row",
                    children=[dcc.Graph(className="graph", id="network-graph")],
                ),
            ],
        ),
        dcc.Interval(
            id="refresh-interval", interval=1, n_intervals=0  # (in milliseconds)
        ),
    ]
)
