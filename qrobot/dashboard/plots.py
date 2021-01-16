import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import dash_table
import dash_html_components as html
import pandas as pd

from ..core import Core


def bar_all_bursts():

    df = []
    for qunit in Core():
        name = qunit.name
        burst = qunit.burst()
        df.append([name, burst])

    df = pd.DataFrame(df, columns=["name", "burst"])

    fig = px.bar(df, x='name', y='burst')

    #fig = {
    #    'data': [
    #        {
    #            'x': df['name'],
    #            'y': df['burst'],
    #            'name': "Qunits",
    #            'type': 'histogram'
    #        },
    #    ],
    #    'layout': go.Layout(
    #        xaxis={'type': 'category', 'title': 'Qunits'},
    #        yaxis={'type': 'linear', 'title': 'Bursts'},
    #        margin={'r': 0, 't': 0, 'l': 100, 'b': 100, 'pad': 0},
    #        legend={'x': 0, 'y': 1},
    #        showlegend=False,
    #        hovermode='closest',
    #        plot_bgcolor='rgba(0,0,0,0)',
    #        paper_bgcolor='rgba(0,0,0,0)',
    #   )
    #}
    return fig


def qunits_table():
    df = []
    for qunit in Core():
        df.append([
            qunit.name,
            qunit.n,
            qunit.tau,
            qunit.Ts,
            qunit.query()
        ])
    df = pd.DataFrame(df, columns = ["name", "n", "tau", "Ts", "query"])
    return html.Div([
        dash_table.DataTable(
            id='typing_formatting_1',
            data=df.to_dict('rows'),
            columns=[{
                'id': 'name',
                'name': 'Name',
                'type': 'text'
            }, {
                'id': 'n',
                'name': 'n',
                'type': 'text'
            }, {
                'id': 'tau',
                'name': 'tau',
                'type': 'text'
            }, {
                'id': 'Ts',
                'name': 'Ts',
                'type': 'text'
            }, {
                'id': 'query',
                'name': 'Query',
                'type': 'text'
            }],
            editable=False
        )
    ])