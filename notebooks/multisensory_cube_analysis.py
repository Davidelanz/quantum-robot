# pip install ipywidgets
# jupyter nbextension enable --py widgetsnbextension
# jupyter labextension install @jupyter-widgets/jupyterlab-manager
from tqdm.notebook import tqdm

import numpy as np
import pandas as pd
import os
import matplotlib
import matplotlib.pyplot as plt
from qrobot.models import AngularModel, LinearModel, BurstAModel


def input_dataset(sample_ratio=1, n=3):

    from itertools import combinations_with_replacement, permutations

    # Generate the range of values
    values = np.arange(0, 1, 1/sample_ratio)
    # Add the other range bound
    values = np.append(values, 1)

    # Avoid results like 0.30000000000000004
    values = [round(x, 10) for x in values]

    # Then generate all the possible combinations of n of these values
    # and their permutations
    data_list = list()
    comb = combinations_with_replacement(values, n)
    for c in comb:
        perm = permutations(c)
        for p in perm:
            data_list.append(p)

    # Delete then the duplicate elements
    dataset = list(dict.fromkeys(data_list))

    # Convert it as a dataframe
    df = pd.DataFrame(dataset, columns=['x1', 'x2', 'x3'])

    # df.sort_values(by=['x1'], inplace=True)

    return df


def test_model(model, target, sample_ratio=10):

    datapath = f"data/df_{type(model).__name__}_n{model.n}_tau{model.tau}_target{target}_sr{sample_ratio}.csv"

    if os.path.isfile(datapath):
        print("Test already made, available at \"" + datapath + "\"")
        return

    df_input = input_dataset(sample_ratio)
    print("Dataset generated!")

    states_list = ["000", "001", "010", "100", "011", "110", "101", "111"]
    shots = pow(10, 5)

    iteration = 1
    tot_iter = len(df_input)
    print(f"The dataset contains {tot_iter} entries.")

    # Initialize the results list
    results_list = list()

    with tqdm(total=tot_iter) as pbar:
        for index, row in df_input.iterrows():

            # Prepare this iteration's entry of the results_list
            result_row = list()

            # Get the distance from the target for this input [x1, x2, x3]
            dist = np.linalg.norm(np.array(row)-np.array(target))
            # The distance is normalized on the hypercube's diagonal
            dist = dist/np.sqrt(model.n)
            # Add target and distace as first and second entry of the result_row
            for t in target:
                result_row.append(t)
            result_row.append(dist)

            # Clear the model for a new iteration
            model.clear()
            # Encode the input
            for i in range(model.n):
                model.encode(row[i], i+1)  # dimensions start at 1, not at 0!
            # Make the query
            model.query(target)
            # Simulate the measurement counts
            counts = model.measure(shots)
            # Convert counts in probabilities and store them
            for key in states_list:
                try:
                    result_row.append(counts[key]/shots)
                except KeyError:
                    result_row.append(0)

            # Then add the row to the result_list
            results_list.append(result_row)
            # and update the progress bar
            pbar.update(1)
            iteration += 1

    # Add labels
    header = ["target_1", "target_2", "target_3", "dist"]
    for state in states_list:
        header.append(state)
    # Convert result list to a dataframe
    df_result = pd.DataFrame(results_list, columns=header)

    # Attach the result to the input dataframe
    df = pd.concat([df_input, df_result], axis=1)
    # and save it to a file
    df.to_csv(datapath, index=False)

    return df


def data_4dplot(datafile, state, fig, n_rows=1, n_cols=1, index=1):
    df = pd.read_csv(datafile)
    ax = fig.add_subplot(n_rows, n_cols, index, projection='3d')

    # 3 Axis (3 dimensions)
    x = df["x1"]
    y = df["x2"]
    z = df["x3"]
    # Colour (4th dimension)
    c = df[state]
    # c = df.iloc[:,11]

    cbar = ax.scatter(x, y, z, c=c, cmap=plt.get_cmap(
        'binary'), vmin=0, vmax=1, alpha=1)
    ax.set_xlabel('x1')
    ax.set_ylabel('x2')
    ax.set_zlabel('x3')
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    ax.set_zlim([0, 1])

    # Plot the query target as a point
    ax.scatter(df["target_1"][0], df["target_2"][0],
               df["target_3"][0], c="blue", linewidths=20, marker="P")

    target = "[{}, {}, {}]".format(
        df["target_1"][0], df["target_2"][0], df["target_3"][0])
    ax.set_title(f"{state} - Target = {target}")

    return cbar


def plot_all_states_4d(datafile):
    fig = plt.figure(figsize=(16, 16))

    cbar = data_4dplot(datafile, "000", fig, 3, 3, 1)
    cbar = data_4dplot(datafile, "001", fig, 3, 3, 2)
    cbar = data_4dplot(datafile, "010", fig, 3, 3, 3)
    cbar = data_4dplot(datafile, "011", fig, 3, 3, 4)
    cbar = data_4dplot(datafile, "100", fig, 3, 3, 5)
    cbar = data_4dplot(datafile, "101", fig, 3, 3, 6)
    cbar = data_4dplot(datafile, "110", fig, 3, 3, 7)
    cbar = data_4dplot(datafile, "111", fig, 3, 3, 8)

    fig.add_subplot(339).axis('off')
    fig.colorbar(cbar)


def plot_states_on_dist(datafile):
    df = pd.read_csv(datafile)
    fig = plt.figure(figsize=(15, 6))

    ax = plt.subplot(1, 1, 1)

    ax.plot(df["dist"], df["000"], 'bo', alpha=.3)
    ax.plot(df["dist"], df["001"]+df["010"]+df["100"], 'yo', alpha=.3)
    ax.plot(df["dist"], df["011"]+df["110"]+df["101"], 'go', alpha=.3)
    ax.plot(df["dist"], df["111"], 'ro', alpha=.3)

    ax.legend(["|000>", "2 zeros", "1 zero", "|111>"])

    target = "[{}, {}, {}]".format(
        df["target_1"][0], df["target_2"][0], df["target_3"][0])
    ax.set_title(
        f"Aggregated probabilities - Target = {target} (dataset = \"{datafile}\")")
    ax.set_xlabel(f"Euclidean distance from {target}")
    ax.set_ylabel("State's measurement probability")


def test_burst_amplification(model, max_ampl, target, sample_ratio=10, shots=pow(10, 5)):

    datapath = f"data/df_BurstAmplification_n{model.n}_tau{model.tau}_target{target}_sr{sample_ratio}.csv"

    if os.path.isfile(datapath):
        print("Test already made, available at \"" + datapath + "\"")
        return

    df_input = input_dataset(sample_ratio)
    print("Dataset generated!")

    iteration = 1
    tot_iter = len(df_input)
    print(f"The dataset contains {tot_iter} entries.")

    # Initialize the results list
    results_list = list()

    with tqdm(total=tot_iter*shots*(max_ampl+1)) as pbar:
        for _, row in df_input.iterrows():

            # Prepare this iteration's entry of the results_list
            result_row=list()

            # Get the distance from the target for this input [x1, x2, x3]
            dist=np.linalg.norm(np.array(row)-np.array(target))
            # The distance is normalized on the hypercube's diagonal
            dist=dist/np.sqrt(model.n)

            # Add target and distace as first and second entry of the result_row
            for t in target:
                result_row.append(t)
            result_row.append(dist)

            # Simulate "shots" bursts
            bursts=list()
            for _ in range(shots):
                model.clear()
                # Encode the input
                for i in range(model.n):
                    # dimensions start at 1, not at 0!
                    model.encode(row[i], i+1)
                # Make the query
                model.query(target)
                # Get a burst
                burst=model.decode()
                # Put it in the bursts list
                bursts.append(burst)
                # Update progress bar
                pbar.update(1)

            # Append the mean burst as a result
            avg_burst=np.mean(bursts)
            result_row.append(avg_burst)

            # Amplify the model results
            ampli=BurstAModel(1, 1)
            for ampl in range(1, max_ampl+1):
                bursts=list()
                for _ in range(shots):
                    ampli.clear()
                    # Encode the input
                    ampli.encode(avg_burst, 1)
                    # Get a burst
                    burst=model.decode()
                    # Put it in the bursts list
                    bursts.append(burst)
                    # Update progress bar
                    pbar.update(1)
                avg_burst=np.mean(bursts)
                result_row.append(avg_burst)

            # Then add the row to the result_list
            results_list.append(result_row)

    # Add labels
    header=["target_1", "target_2", "target_3", "dist"]
    for ampl in range(0, max_ampl+1):
        header.append(f"{ampl}-th amplification")
    # Convert result list to a dataframe
    df_result=pd.DataFrame(results_list, columns=header)

    # Attach the result to the input dataframe
    df=pd.concat([df_input, df_result], axis=1)

    # Save it to a file
    df.to_csv(datapath, index=False)

    return df


def plot_all_amplifications_4d(datafile, max_ampl=10):
    fig=plt.figure(figsize=(16, 16))
    for i in range(1, max_ampl+2):
        cbar=data_4dplot(datafile, f"{i-1}-th amplification", fig, 4, 3, i)

    fig.add_subplot(4, 3, max_ampl+2).axis('off')
    fig.colorbar(cbar)


def plot_ampli_on_dist(datafile, max_ampl=10):
    df=pd.read_csv(datafile)
    fig=plt.figure(figsize=(15, 6))

    ax=plt.subplot(1, 1, 1)

    legend=list()

    for i in range(max_ampl+1):
        ax.plot(df["dist"], df[f"{i}-th amplification"], 'o', alpha=.3)
        legend.append(f"{i}-th amplification")

    ax.legend(legend)

    target="[{}, {}, {}]".format(
        df["target_1"][0], df["target_2"][0], df["target_3"][0])
    ax.set_title(
        f"Average bursts - Target = {target} (dataset = \"{datafile}\")")
    ax.set_xlabel(f"Euclidean distance from {target}")
    ax.set_ylabel("Average burst")
