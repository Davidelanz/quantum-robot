# Install quantum-robot

Install the core package with pip:

```console
pip install -U quantum-robot
```

Optional functionality is provided by extras in the same distribution:

```console
pip install -U "quantum-robot[qunits]"
pip install -U "quantum-robot[visualization]"
pip install -U "quantum-robot[dashboard]"
```

The corresponding Python imports are `qrobot_qunits`,
`qrobot_visualization`, and `qrobot_dashboard`. Extras install only the
dependencies for that capability; all import packages are shipped from the
same source tree.

For development from a checkout, Poetry creates and manages the environment:

```console
git clone https://github.com/Davidelanz/quantum-robot.git
cd quantum-robot
poetry install --extras test --extras docs --extras model-visualization --extras qunits --extras visualization --extras dashboard
```
