import os
from pathlib import Path

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
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
                id='slider-refresh',
                min=0,
                max=1,
                step=0.001,
                value=1,
            ),
            html.Div(id='slider-refresh-output')
        ]),
        html.H2(children="Bursts"),
        html.Div(className="row", children=[
            dcc.Loading(
                className="graph",
                id="loading-bar-all-bursts",
                type="default",
                fullscreen=False,
                children=[dcc.Graph(id='bar-all-bursts')],
            ),
        ]),
    ]),
    dcc.Interval(
        id='interval-component',
        interval=1,  # (in milliseconds)
        n_intervals=0
    )
])


@app.callback(Output('bar-all-bursts', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_bar_all_bursts(in1):
    figure = bar_all_bursts()
    return figure


@app.callback(Output('interval-component', 'interval'),
              [Input('slider-refresh', 'value')])
def update_interval_rate(refresh_value):
    return refresh_value*1000
