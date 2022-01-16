"""
    These functions are made to test and compare different models
"""

import pandas as pd
import matplotlib.pyplot as plt


def test_input(
    model, input_samples, tau=1, x_label="input",
):
    dataframe = pd.DataFrame()
    shots = 1000000

    inputs = [s / input_samples for s in range(0, input_samples + 1)]

    for i in inputs:

        print(f"Input = {i}  ", end="\r")
        model.clear()

        # Encode the input and measure
        for _ in range(0, tau):
            model.encode(i, dim=0)
        counts = model.measure(shots)

        # Store in the dataset (normalizing probabilities)
        counts[x_label] = i
        try:
            counts["0"] = counts["0"] / shots
        except KeyError:
            counts["0"] = 0
        try:
            counts["1"] = counts["1"] / shots
        except KeyError:
            counts["1"] = 0
        dataframe = dataframe.append(counts, ignore_index=True)

    print("                        ")
    return dataframe


def test_tau_up(model, intensity=1, x_label="tau_up"):
    dataframe = pd.DataFrame()
    shots = 1000000

    for tau_up in range(0, model.tau + 1):

        print(f"Tau_up = {tau_up}/{model.tau}    ", end="\r")
        model.clear()

        # Encode the tau_up events
        for _ in range(0, tau_up):
            model.encode(intensity, dim=0)
        counts = model.measure(shots)

        # Store in the dataset (normalizing probabilities)
        counts[x_label] = tau_up
        try:
            counts["0"] = counts["0"] / shots
        except KeyError:
            counts["0"] = 0
        try:
            counts["1"] = counts["1"] / shots
        except KeyError:
            counts["1"] = 0
        dataframe = dataframe.append(counts, ignore_index=True)

    print("                        ")
    return dataframe


def test_query(model, query_samples, x_label="query"):
    dataframe = pd.DataFrame()
    shots = 1000000

    queries = [s / query_samples for s in range(0, query_samples + 1)]

    for query in queries:

        print(f"Query = {query}  ", end="\r")
        model.clear()

        # Encode always .5 events
        model.encode(0.5, dim=0)
        # then apply the query
        model.query([query])
        # and measure
        counts = model.measure(shots)

        # Store in the dataset (normalizing probabilities)
        counts[x_label] = query
        try:
            counts["0"] = counts["0"] / shots
        except KeyError:
            counts["0"] = 0
        try:
            counts["1"] = counts["1"] / shots
        except KeyError:
            counts["1"] = 0
        dataframe = dataframe.append(counts, ignore_index=True)

    print("                        ")
    return dataframe


def plot_versus(dataframe1, dataframe2, x_label):
    plt.figure(figsize=(15, 4), dpi=150)
    plt.grid(linestyle="--", linewidth=1)

    plt.subplot(1, 2, 1)
    dataframe1.plot(x=x_label, y=["0", "1"], kind="line", ax=plt.gca())
    plt.legend(["|0>", "|1>"])
    plt.grid()

    plt.subplot(1, 2, 2)
    dataframe2.plot(x=x_label, y=["0", "1"], kind="line", ax=plt.gca())
    plt.legend(["|0>", "|1>"])
    plt.grid()

    plt.show()
