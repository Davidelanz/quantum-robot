from dash import dcc, html

layout = html.Div(children=[
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
