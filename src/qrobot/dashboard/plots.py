"""
Dashboard utilities for plotting.
"""

import pandas as pd
import plotly.graph_objs as go

from ..qunits.redis_utils import redis_status


def bar_all_bursts():
    """Barplot of all bursts."""
    status = {}
    status["qunit"] = []
    status["burst"] = []
    for key, value in redis_status().items():
        key = key.decode("ascii")
        if "state" not in key:
            status["qunit"].append(key)
            status["burst"].append(float(value))

    burst_df = pd.DataFrame(status).sort_values("qunit")

    # Use textposition='auto' for direct text
    fig = go.Figure(
        data=[
            go.Bar(
                x=burst_df["qunit"],
                y=burst_df["burst"],
                text=burst_df["burst"],
                textposition="auto",
            )
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
