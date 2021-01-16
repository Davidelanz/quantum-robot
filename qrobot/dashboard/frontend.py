import os
from flask import Flask, request
from pathlib import Path
import json

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State
from .plots import bar_all_bursts, qunits_table

from ..core import Core

ROOT_DIR = Path(__file__).parent
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")

server = Flask('Quantum-robot Dashboard')
app = dash.Dash(
    'Quantum-robot Dashboard',
    assets_folder=ASSETS_DIR,
    server=server)


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@server.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'


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
        html.Div(className="row", id="core-details", children=[]),
    ]),
    # Hidden divs inside the app storing intermediate values
    html.Div(id='qunits', style={'display': 'none'}),
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


@app.callback(Output('core-details', 'children'),
              Input('interval-component', 'n_intervals'))
def update_bar_all_bursts(in1):
    return qunits_table()


@app.callback(Output('interval-component', 'interval'),
              [Input('slider-refresh', 'value')])
def update_interval_rate(refresh_value):
    return refresh_value*1000


@app.callback(Output('slider-refresh-output', 'children'),
              [Input('interval-component', 'n_intervals')],
              state=[State('slider-refresh', 'value')])
def update_minTs(in1, refresh_value):
    Ts_list = [qunit.Ts for qunit in Core()]
    if Ts_list:
        return f"Refresh period: {refresh_value*1000}ms | "\
            f"(min Ts: {min(Ts_list)*1000}ms)"
    else:
        return f"Refresh: {refresh_value*1000}ms | "\
            "No qunits"
