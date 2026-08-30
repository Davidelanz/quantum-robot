---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.5
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Multidimensional Angular Model (RGB visualization)

```{admonition} Research provenance
This notebook accompanies [*Multi-sensory Integration in a Quantum-Like Robot
Perception Model*](https://doi.org/10.1007/978-3-030-71151-1_44), published in
*Experimental Robotics* (2021); the preprint is
[arXiv:2006.16404](https://arxiv.org/abs/2006.16404). Its RGB visualizations are
paper-specific and intentionally remain in this notebook.
```

```{code-cell} ipython3
import matplotlib.pyplot as plt
import numpy as np

from qrobot.bursts import ZeroBurst
from qrobot.models import AngularModel
```

In this notebook we present a 3-dimensional ($n=3$) demo for the
`AngularModel` class. For simplicity, we consider $\tau = 1$.

```{code-cell} ipython3
n = 3
tau = 1
```

> *Note*: The RGB analogy provides an intuitive picture of three normalized
sensor channels; it is a visualization device, not a claim that the model
learns a color concept.

## Input definition

We start by defining an arbitrary normalized three-channel input:

```{code-cell} ipython3
input_data = [0.1, 0.5, 0.9]
```

```{code-cell} ipython3
:tags: [hide-input]

def plot_rgb_input(data):
    """Plot a normalized three-channel input in RGB space and as a color."""
    fig = plt.figure(figsize=(10, 3))
    rgb_axis = fig.add_subplot(1, 2, 1, projection="3d")
    rgb_axis.scatter(*data, color=[data], marker="o", s=80)
    rgb_axis.set(
        xlabel="Red",
        ylabel="Green",
        zlabel="Blue",
        xlim=(0, 1),
        ylim=(0, 1),
        zlim=(0, 1),
    )

    color_axis = fig.add_subplot(1, 2, 2)
    color_axis.imshow(np.asarray(data)[np.newaxis, np.newaxis, :])
    color_axis.set_title(f"RGB input = {data}")
    color_axis.set_axis_off()
    plt.show()
```

```{code-cell} ipython3
plot_rgb_input(input_data)
```

## Encode the input in the model

We initialize the model by instantiating an object with $n$ and $\tau$

```{code-cell} ipython3
model = AngularModel(n, tau)
```

Encoding a general multidimensional sequence requires one call per temporal
sample. The model maps each vector element to its corresponding dimension. This
example has $\tau = 1$, so the single event requires one encoding call:

```{code-cell} ipython3
model.clear()  # Keep this cell repeatable by discarding any earlier encoding.
model.encode_vector(input_data)
```

The model is implemented by a Qiskit quantum circuit:

```{code-cell} ipython3
model.print_circuit()
```

Given the input we defined above, the model is in the following state:

```{code-cell} ipython3
:tags: [hide-input]

def plot_encoded_model_state(encoded_model):
    """Plot the encoded statevector and density matrix."""
    encoded_model.plot_state_mat()
```

```{code-cell} ipython3
plot_encoded_model_state(model)
```

## Measurement simulation

We simulate ``shots`` measurements, and then we extract the relative frequencies for the $2^n$ possible basis state outcomes:

```{code-cell} ipython3
shots = 1000000
counts = model.measure(shots)
```

Raw counts for each possible outcome:

```{code-cell} ipython3
import json

print("Aggregated binary outcomes of the circuit:")
print(json.dumps(counts, sort_keys=True, indent=4))
```

From the raw counts we can obtain the relative frequencies (aka the probabilities) and compare them with the input sequence. Since we have not operated any change of basis (with the ``model.query(target)`` method), the canonical basis is maintained, and it is possible to visualize it still with our RGB representation:

```{code-cell} ipython3
:tags: [hide-input]

def plot_canonical_measurements(data, measurement_counts, measurement_shots):
    """Plot the input and canonical-basis outcome probabilities as RGB tiles."""
    states = [f"{index:03b}" for index in range(8)]
    fig, axes = plt.subplots(1, 9, figsize=(15, 2), dpi=150)

    tiles = [("Input", data, "")] + [
        (
            f"|{state}⟩",
            [float(bit) for bit in reversed(state)],
            f"{measurement_counts.get(state, 0) / measurement_shots:.1%}",
        )
        for state in states
    ]
    for axis, (title, color, probability) in zip(axes, tiles, strict=True):
        axis.imshow(np.asarray(color)[np.newaxis, np.newaxis, :])
        axis.set_title(title)
        axis.set_xlabel(probability)
        axis.set_xticks([])
        axis.set_yticks([])
    plt.show()
```

```{code-cell} ipython3
plot_canonical_measurements(input_data, counts, shots)
```

This shows how the two states which are more likely to be measured are the "blue" $|100\rangle$ and "cyan" $|110\rangle$ ones, which are the closes to our "blue-ish" input.

## Measurement changes w.r.t. varying input

We can now move the input through RGB space and observe how the probability of
each canonical basis state changes. We define this set of inputs:

```{code-cell} ipython3
input_positions = np.linspace(0, 1, 101)
path_positions = np.linspace(0, 1, 6)
path_colors = np.asarray(
    [
        [0.0, 0.0, 0.0],  # black
        [0.2, 0.9, 0.1],  # green-ish
        [1.0, 1.0, 1.0],  # white
        [0.9, 0.2, 0.1],  # red-ish
        [0.2, 0.1, 0.9],  # blue-ish
        [0.0, 0.0, 0.0],  # black
    ]
)
input_colors = np.column_stack(
    [np.interp(input_positions, path_positions, path_colors[:, channel]) for channel in range(3)]
)
```

```{code-cell} ipython3
:tags: [hide-input]

def plot_input_color_path(colors, stops):
    """Render the complete RGB input path as a standalone color strip."""
    fig, axis = plt.subplots(figsize=(15, 2), dpi=150)
    axis.imshow(
        np.asarray(colors)[np.newaxis, :, :],
        aspect="auto",
        extent=(0, 1, 0, 1),
        interpolation="bilinear",
    )
    axis.set_xticks(
        stops,
        ["black", "green-ish", "white", "red-ish", "blue-ish", "black"],
    )
    axis.set_yticks([])
    axis.set_title("RGB input path")
    axis.set_xlabel("Position along the input path")
    plt.show()
```

```{code-cell} ipython3
plot_input_color_path(input_colors, path_positions)
```

The color strip renders the input at every position. We now want to see how the
probabilities of measuring each of the eight canonical basis states changes with
the input. For every point on the input domain, we create a fresh model, encode
its three RGB components, and read the exact probability of every basis state
from the statevector:

```{code-cell} ipython3
state_labels = [f"{index:03b}" for index in range(8)]
canonical_probabilities = {state: [] for state in state_labels}
state_rgb_colors = {state: tuple(float(bit) for bit in reversed(state)) for state in state_labels}

for input_color in input_colors:
    sliding_model = AngularModel(n=3, tau=1)
    for dim, value in enumerate(input_color):
        sliding_model.encode(value, dim)
    probabilities = np.abs(sliding_model.get_statevector()) ** 2
    for index, state in enumerate(state_labels):
        canonical_probabilities[state].append(probabilities[index])
```

```{code-cell} ipython3
:tags: [hide-input]

import matplotlib.patheffects as path_effects


def plot_canonical_input_sweep(positions, colors, state_probabilities, state_colors):
    """Plot an RGB input path in the unqueried canonical basis."""
    linestyles = ["-", "-", "-", "-", "-", "-", "-", "-"]
    markers = ["o", "s", "^", "v", "D", "P", "X", "*"]
    fig, axis = plt.subplots(figsize=(13, 10))
    for index, state in enumerate(state_labels):
        (line,) = axis.plot(
            positions,
            state_probabilities[state],
            color=state_colors[state],
            linestyle=linestyles[index],
            marker=markers[index],
            markevery=(index * 2, 18),
            markersize=9,
            linewidth=2,
            alpha=0.5,
            zorder=2 + index,
            label=f"|{state}⟩",
        )
        if state in {"000", "111"}:
            outline = "white" if state == "000" else "black"
            line.set_path_effects(
                [
                    path_effects.Stroke(linewidth=0.5, foreground=outline),
                    path_effects.Normal(),
                ]
            )

    input_gradient = np.asarray(colors)[np.newaxis, :, :]
    axis.imshow(
        input_gradient,
        aspect="auto",
        extent=(0, 1, -0.20, -0.10),
        transform=axis.get_xaxis_transform(),
        clip_on=False,
        interpolation="bilinear",
    )
    axis.set(
        xlabel="Position along the RGB input path",
        ylabel="Exact state probability",
        xlim=(0, 1),
        ylim=(0, 1),
        title="Canonical-basis response along an RGB input path",
    )
    axis.xaxis.labelpad = 35
    axis.set_xticks(
        np.linspace(0, 1, 6),
        ["black", "green-ish", "white", "red-ish", "blue-ish", "black"],
    )
    axis.tick_params(axis="x", pad=35)
    axis.grid(alpha=0.3)
    axis.legend(ncols=4)
    fig.subplots_adjust(bottom=0.25)
    plt.show()
```

```{code-cell} ipython3
plot_canonical_input_sweep(input_positions, input_colors, canonical_probabilities, state_rgb_colors)
```

As the input reaches each color stop, probability concentrates on the nearest
canonical RGB corner: $|000\rangle$ at black, $|010\rangle$ near green,
$|111\rangle$ at white, $|001\rangle$ near red, and $|100\rangle$ near blue.
Between those stops, several basis states remain probable because each channel
is encoded continuously rather than rounded to `0` or `1`. Some curves overlap
when different states receive the same probability; their distinct markers
make those coincident outcomes visible.

## Querying for similarity to a color

Now keep a warm-red input fixed and compare it with a blue query:

```{code-cell} ipython3
fixed_input = [0.9, 0.2, 0.1]
fixed_query = [0.2, 0.2, 0.7]
```

```{code-cell} ipython3
:tags: [hide-input]

def plot_fixed_input_and_query(input_color, query_color):
    """Display the fixed RGB input and query as color swatches."""
    fig, axes = plt.subplots(1, 9, figsize=(15, 2), dpi=150)
    for axis, title, color in zip(
        axes[[0, 2]],
        (f"Input {input_color}", f"Query {query_color}"),
        (input_color, query_color),
        strict=True,
    ):
        axis.imshow(np.asarray(color)[np.newaxis, np.newaxis, :])
        axis.set_title(title)
    for axis in axes:
        axis.set_axis_off()
    plt.show()
```

```{code-cell} ipython3
plot_fixed_input_and_query(fixed_input, fixed_query)
```

A query changes the basis in which the encoded input is measured. Given a
normalized target color $\bar{\mathbf{x}}$, it applies an inverse rotation to
every qubit:

$$
Q(\bar{\mathbf{x}})=\bigotimes_i R_y(-\pi\bar{x}_i).
$$

This maps an input equal to the query onto $|000\rangle$. After this basis
change, the state vectors can no longer be mapped to an RGB color. For each channel,
alignment makes the `0` outcome more probable and mismatch makes the `1` outcome more
probable. After measuring a state, `ZeroBurst` converts its zero-bit fraction
into a match intensity: how closely the sampled outcome matches the query.

$$
B_0(s)=\frac{\text{number of zeros in }s}{3}.
$$

`OneBurst` provides the complementary mismatch intensity: the sampled outcome's
fraction of bits that differ from the query-mapped zero state.

The next cell encodes a fixed input, applies the query transformation, and
samples the queried model:

```{code-cell} ipython3
queried_model = AngularModel(n=3, tau=1)
for dim, value in enumerate(fixed_input):
    queried_model.encode(value, dim)
queried_model.query(fixed_query)

query_shots = 100_000
queried_counts = queried_model.measure(query_shots)
```

```{code-cell} ipython3
:tags: [hide-input]

def plot_queried_measurements(query_color, measurement_counts, measurement_shots):
    """Plot queried outcomes using copper intensity for ZeroBurst values."""
    heat_map = plt.colormaps["copper"]
    states = [f"{index:03b}" for index in range(8)]
    fig, axes = plt.subplots(1, 9, figsize=(15, 2), dpi=150)

    axes[0].imshow(np.asarray(query_color)[np.newaxis, np.newaxis, :])
    axes[0].set_title("Query")
    axes[0].set_xlabel(str(query_color))
    axes[0].set_xticks([])
    axes[0].set_yticks([])

    for axis, state in zip(axes[1:], states, strict=True):
        burst = ZeroBurst()(state)
        probability = measurement_counts.get(state, 0) / measurement_shots
        axis.imshow(np.asarray(heat_map(burst))[np.newaxis, np.newaxis, :])
        axis.set_title(f"|{state}⟩")
        axis.set_xlabel(f"P={probability:.1%}\nB₀={burst:.2f}")
        axis.set_xticks([])
        axis.set_yticks([])
    plt.show()
```

```{code-cell} ipython3
plot_queried_measurements(fixed_query, queried_counts, query_shots)
```

The tile color now represents "how much the input is similar to my query"
(that is, the `ZeroBurst` value). With the color code we used here, darker
copper means fewer matching channels, and lighter copper means
more. The probability $P$ answers “how likely is this pattern?”,
while $B_0$ answers “what match intensity is emitted if this pattern is
sampled?”


## Measurement changes w.r.t. varying query (with fixed input)

We can now hold the same input constant while moving the query through RGB
space. First, recall the fixed warm-red input:

```{code-cell} ipython3
:tags: [hide-input]

def plot_varying_query_input(input_color):
    """Display the fixed input used throughout the query sweep."""
    fig, axes = plt.subplots(1, 9, figsize=(15, 2), dpi=150)
    axis = axes[0]
    axis.imshow(np.asarray(input_color)[np.newaxis, np.newaxis, :])
    axis.set_title(f"Fixed input {input_color}")
    axis.set_axis_off()
    for unused_axis in axes[1:]:
        unused_axis.set_axis_off()
    plt.show()
```

```{code-cell} ipython3
plot_varying_query_input(fixed_input)
```

The query follows a piecewise RGB path from blue to red and then from red to
green. Pure red, at the middle of the axis, is the closest point on this path
to the warm-red input. The blue and green endpoints each disagree with it
strongly in two channels.

```{code-cell} ipython3
query_positions = np.linspace(0, 1, 101)

query_colors = []
for position in query_positions:
    if position <= 0.5:
        blend = 2 * position
        query_colors.append([blend, 0.0, 1.0 - blend])  # blue -> red
    else:
        blend = 2 * (position - 0.5)
        query_colors.append([1.0 - blend, blend, 0.0])  # red -> green

queried_probabilities = {state: [] for state in state_labels}
zero_burst_scores = {state: ZeroBurst()(state) for state in state_labels}
```

```{code-cell} ipython3
:tags: [hide-input]

def plot_query_color_path(colors):
    """Render the blue–red–green query path as a standalone color strip."""
    fig, axis = plt.subplots(figsize=(15, 2), dpi=150)
    axis.imshow(
        np.asarray(colors)[np.newaxis, :, :],
        aspect="auto",
        extent=(0, 1, 0, 1),
        interpolation="bilinear",
    )
    axis.set_xticks([0, 0.5, 1], ["blue", "red", "green"])
    axis.set_yticks([])
    axis.set_title("RGB query path")
    axis.set_xlabel("Position along the query path")
    plt.show()
```

```{code-cell} ipython3
plot_query_color_path(query_colors)
```

At every position we re-encode the unchanged input in a fresh model, apply the
current query color, and record the exact statevector probabilities after the
basis change:

```{code-cell} ipython3
for query_color in query_colors:
    queried_model = AngularModel(n=3, tau=1)
    for dim, value in enumerate(fixed_input):
        queried_model.encode(value, dim)
    queried_model.query(query_color)
    probabilities = np.abs(queried_model.get_statevector()) ** 2
    for index, state in enumerate(state_labels):
        queried_probabilities[state].append(probabilities[index])
```

```{code-cell} ipython3
:tags: [hide-input]

def plot_color_query_sweep(positions, colors, fixed_color, state_probabilities, burst_scores):
    """Plot queried outcomes, coloring each state by its ZeroBurst score."""
    heat_map = plt.colormaps["copper"]
    normalization = plt.Normalize(0, 1)
    markers = ["o", "s", "^", "v", "D", "P", "X", "*"]

    fig, axis = plt.subplots(figsize=(13, 10))
    for index, state in enumerate(state_labels):
        score = burst_scores[state]
        axis.plot(
            positions,
            state_probabilities[state],
            color=heat_map(normalization(score)),
            linestyle="-",
            marker=markers[index],
            markevery=(index * 2, 18),
            markersize=9,
            linewidth=2,
            alpha=0.5,
            zorder=2 + index,
            label=f"|{state}⟩  B₀={score:.2f}",
        )

    query_gradient = np.asarray(colors)[np.newaxis, :, :]
    axis.imshow(
        query_gradient,
        aspect="auto",
        extent=(0, 1, -0.20, -0.10),
        transform=axis.get_xaxis_transform(),
        clip_on=False,
        interpolation="bilinear",
    )
    axis.text(
        0.02,
        0.96,
        f"Fixed input: {fixed_color}",
        transform=axis.transAxes,
        va="top",
        color="white",
        fontweight="bold",
        bbox={
            "boxstyle": "round,pad=0.4",
            "facecolor": fixed_color,
            "edgecolor": "white",
        },
    )
    axis.set(
        ylabel="Exact state probability",
        xlim=(0, 1),
        ylim=(0, 1),
        title="Fixed warm-red input queried along a blue–red–green path",
    )
    axis.set_xticks([0, 0.5, 1], ["blue query", "red query", "green query"])
    axis.tick_params(axis="x", pad=55)
    axis.grid(alpha=0.3)
    axis.legend(ncols=3, fontsize="small")

    color_scale = plt.cm.ScalarMappable(norm=normalization, cmap=heat_map)
    color_scale.set_array([])
    fig.colorbar(color_scale, ax=axis, label="ZeroBurst match intensity B₀")
    fig.subplots_adjust(bottom=0.38)
    plt.show()
```

```{code-cell} ipython3
plot_color_query_sweep(
    query_positions,
    query_colors,
    fixed_input,
    queried_probabilities,
    zero_burst_scores,
)
```

The height of a state curve gives the probability of measuring that state. Its
copper heat color gives the `ZeroBurst` value emitted if that state is sampled.
The color therefore describes how strongly that particular outcome matches
the query.

Around the red query, states with higher match intensities become more
probable. Farther from red, lower-match outcomes become more likely.

We can summarize the complete measurement distribution at every query by
treating each possible `ZeroBurst` value as a random outcome. The mean is the
average match intensity expected over repeated measurements, while the
standard deviation describes how much individual sampled bursts vary around
that mean:

```{code-cell} ipython3
burst_means = []
burst_standard_deviations = []

for position_index in range(len(query_positions)):
    probabilities = np.asarray(
        [queried_probabilities[state][position_index] for state in state_labels]
    )
    burst_values = np.asarray([zero_burst_scores[state] for state in state_labels])
    mean = np.sum(probabilities * burst_values)
    variance = np.sum(probabilities * (burst_values - mean) ** 2)
    burst_means.append(mean)
    burst_standard_deviations.append(np.sqrt(variance))
```

```{code-cell} ipython3
:tags: [hide-input]

def plot_burst_summary(positions, colors, means, standard_deviations):
    """Plot mean ZeroBurst intensity with a continuous ±1σ band."""
    means = np.asarray(means)
    standard_deviations = np.asarray(standard_deviations)
    lower_bound = np.clip(means - standard_deviations, 0, 1)
    upper_bound = np.clip(means + standard_deviations, 0, 1)
    fig, axis = plt.subplots(figsize=(13, 8))
    axis.fill_between(
        positions,
        lower_bound,
        upper_bound,
        color="peru",
        alpha=0.3,
        label="Mean ± 1 standard deviation",
    )
    axis.plot(positions, lower_bound, color="peru", linewidth=1, alpha=0.8)
    axis.plot(positions, upper_bound, color="peru", linewidth=1, alpha=0.8)
    axis.plot(
        positions,
        means,
        color="saddlebrown",
        linewidth=3,
        label="Mean ZeroBurst intensity",
    )
    query_gradient = np.asarray(colors)[np.newaxis, :, :]
    axis.imshow(
        query_gradient,
        aspect="auto",
        extent=(0, 1, -0.20, -0.10),
        transform=axis.get_xaxis_transform(),
        clip_on=False,
        interpolation="bilinear",
    )
    axis.set(
        ylabel="ZeroBurst match intensity",
        xlim=(0, 1),
        ylim=(0, 1),
        title="Mean and variability of the measured match intensity",
    )
    axis.set_xticks([0, 0.5, 1], ["blue query", "red query", "green query"])
    axis.tick_params(axis="x", pad=55)
    axis.grid(alpha=0.3)
    axis.legend()
    fig.subplots_adjust(bottom=0.3)
    plt.show()
```

```{code-cell} ipython3
plot_burst_summary(
    query_positions,
    query_colors,
    burst_means,
    burst_standard_deviations,
)
```

In the plot above, the central line shows the overall output, and the shaded band
shows one standard deviation on either side. The values are computed from exact
state probabilities, so the band represents intrinsic measurement variability
rather than finite-shot sampling noise.


## References

- D. Lanza, P. Solinas, and F. Mastrogiovanni, [*Multi-sensory Integration in
  a Quantum-Like Robot Perception
  Model*](https://doi.org/10.1007/978-3-030-71151-1_44), *Experimental
  Robotics*, 2021; [arXiv:2006.16404](https://arxiv.org/abs/2006.16404).
- D. Lanza, [*Quantum-like Modeling of Cognitive Architectures for
  Robotics*](https://doi.org/10.5281/zenodo.22068511), Zenodo, 2020.
