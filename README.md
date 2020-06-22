# `quantum-robot` Python package

<p> <!--align="center"-->
    <a href="https://www.python.org/downloads/release/python-383/" alt="Python Version">
        <img src="https://img.shields.io/badge/Python-3.8.2-yellow" /></a>
    <a href="https://qiskit.org/documentation/release_notes.html" alt="Qiskit Version">
        <img src="https://img.shields.io/badge/Qiskit-0.19.3-blue" /></a>
    <a href="http://wiki.ros.org/noetic/Installation" alt="ROS Distribution">
        <img src="https://img.shields.io/badge/ROS-noetic-green" /></a>
</p>
</p>

`quantum-robot` is a Python module for quantum-like perception modeling for robotics. The module exploits [Qiksit](https://qiskit.org/) framework for quantum-simulation and backend exectuion and [ROS](https://www.ros.org/) as real-time simulations.

The project was started in 2019 by Davide Lanza as a Master thesis research, with the help of Fulvio Mastrogiovanni and Paolo Solinas.

It is currently maintained by Davide Lanza.

Website: https://quantum-robot.org

```bibtex
@misc{lanza2020preliminary,
    title={A Preliminary Study for a Quantum-like Robot Perception Model},
    author={Davide Lanza and Paolo Solinas and Fulvio Mastrogiovanni},
    year={2020},
    eprint={2006.02771},
    archivePrefix={arXiv},
    primaryClass={cs.RO},
    url={https://arxiv.org/abs/2006.02771}
}
```

## Summary

1. [Installation](#installation)
1. [Development](#development)
1. [Contributing](#contributing)
1. [Credits](#credits)
1. [License](#license)

## Installation[↑](#summary)

### Dependencies

`quantum-robot` requires:
- quantum-robot 0.1 requires 
- qiskit >= 0.19.3 
- opencv-python >= 4.2.0.34
- imutils >= 0.5.3
- pandas >= 1.0.4 
- numpy >= 1.18.5 

`quantum-robot` plotting capabilities (i.e., functions start with plot_ and classes end with "Display") require:
- Matplotlib >= 2.1.1
- scikit-image >= 0.13
- seaborn >= 0.9.0

### User installation
The easiest way to install `quantum-robot` is using `pip`:
```
pip install -U scikit-learn
```

The module can be [installed from source](https://packaging.python.org/tutorials/installing-packages/#id19) as well.


## Testing

After installation, you can launch the test suite from outside the source directory (you will need to have pytest >= 3.3.0 installed):
```
pytest qrobot
```



## Development[↑](#summary)

### The ROS abstract nodes

<p> <!-- align="center"-->
        <img src="./doc/abstract_nodes_flowchart.svg" width=100%/>
</p>


## Contributing[↑](#summary)

## Credits[↑](#summary)

1. Lanza, Solinas, Mastrogiovanni. *A Preliminary Study for a Quantum-like Robot Perception Model* (2020) [[arXiv:2006.02771]](https://arxiv.org/abs/2006.02771)
1. Lanza, Solinas, Mastrogiovanni. *Multi-sensory Integration in a Quantum-Like Robot Perception Model*

## License[↑](#summary)

[MIT](https://github.com/Davidelanz/quantum_robot/blob/master/LICENSE)
