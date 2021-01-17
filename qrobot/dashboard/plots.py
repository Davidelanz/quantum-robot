import pandas as pd
import plotly.graph_objs as go

from ..qunits.qunit import redis_status


def bar_all_bursts():
    status = {}
    status["qunit"] = []
    status["burst"] = []
    for k, v in redis_status().items():
        k = k.decode('ascii')
        if "state" not in k:
            status["qunit"].append(k)
            status["burst"].append(float(v))

    df = pd.DataFrame(status)

    fig = {
        'data': [
            {
                'x': df['qunit'],
                'y': df['burst'],
                'name': "Qunits",
                # 'type': 'histogram'
            },
        ],
        'layout': go.Layout(
            xaxis={'type': 'category', 'title': 'Qunits'},
            yaxis={'type': 'linear', 'title': 'Bursts'},
            margin={'r': 0, 't': 0, 'l': 100, 'b': 100, 'pad': 0},
            legend={'x': 0, 'y': 1},
            showlegend=False,
            hovermode='closest',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
    }
    return fig
