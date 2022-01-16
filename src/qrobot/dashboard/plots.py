"""
Dashboard webapp to monitor current qUnits sharing the redis server.
"""

import pandas as pd
import plotly.graph_objs as go

from ..qunits.qunit import redis_status


def bar_all_bursts():
    status = {}
    status["qunit"] = []
    status["burst"] = []
    for k, v in redis_status().items():
        k = k.decode("ascii")
        if "state" not in k:
            status["qunit"].append(k)
            status["burst"].append(float(v))

    df = pd.DataFrame(status).sort_values("qunit")

    # Use textposition='auto' for direct text
    fig = go.Figure(
        data=[
            go.Bar(x=df["qunit"], y=df["burst"], text=df["burst"], textposition="auto")
        ]
    )

    fig.layout = go.Layout(
        xaxis={"type": "category", "title": "Qunits"},
        yaxis={"type": "linear", "title": "Bursts"},
        margin={"r": 0, "t": 0, "l": 100, "b": 100, "pad": 0},
        showlegend=False,
        yaxis_range=[0, 1],
        # hovermode='closest',
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )

    return fig
