import os
from pathlib import Path

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from flask import Flask, request

from .plots import bar_all_bursts

ROOT_DIR = Path(__file__).parent
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
NAME = "Quantum-robot Dashboard"

server = Flask(NAME)
app = dash.Dash(NAME, assets_folder=ASSETS_DIR, server=server)


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError(f'{NAME} is not running with the Werkzeug Server')
    func()


@server.route('/shutdown', methods=['GET'])
def shutdown():
    shutdown_server()
    return f'{NAME} shutting down...'


app.layout = html.Div(children=[
    html.Div(className="container width60", children=[
        html.H1(children='Quantum-robot Dashboard'),
        html.Div(className="row", children=[
            dcc.Slider(
                id='refresh-slider',
                min=0,
                max=1,
                step=0.001,
                value=1,
            ),
            html.Div(id='refresh-slider-text')
        ]),
        html.H2(children="Bursts"),
        html.Div(className="row", children=[
            dcc.Loading(
                className="loading",
                id="loading-bursts-bar",
                type="default",
                fullscreen=False,
                children=[
                    dcc.Graph(
                        className="graph",
                        id='bursts-bar'
                    )],
            ),
        ]),
    ]),
    dcc.Interval(
        id='refresh-interval',
        interval=1,  # (in milliseconds)
        n_intervals=0
    )
])


@app.callback(
    Output('bursts-bar', 'figure'),
    [Input('refresh-interval', 'n_intervals')])
def update_bar_all_bursts(n_intervals):
    figure = bar_all_bursts()
    return figure


@app.callback(
    Output('refresh-interval', 'interval'),
    [Input('refresh-slider', 'value')])
def update_interval_rate(refresh_value):
    return refresh_value*1000  # seconds to milliseconds


@app.callback(Output('refresh-slider-text', 'children'),
              [Input('refresh-interval', 'n_intervals')],
              state=[State('refresh-slider', 'value')])
def update_refresh_interval(n_intervals, refresh_value):
    return f"Refresh: {refresh_value*1000}ms"


def run_dashboard():
    """Run dashboard at ``http://localhost:8050``.
    To shutdown the dashboard, go to
    ``http://localhost:8050/shutdown``.

    """
    app.run_server(debug=False)
