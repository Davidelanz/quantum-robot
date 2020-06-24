# quantum-robot

<p>    <!--align="center" -->
    <a href="https://travis-ci.com/github/Davidelanz/quantum-robot" alt="Build">
        <img src="https://travis-ci.com/Davidelanz/quantum-robot.svg?token=BnWGyPSEGJoK3Kmq8jGJ&branch=master&status=failed" />
    </a>
    <a href="https://codecov.io/gh/Davidelanz/quantum-robot" alt="Code coverage">
        <img src="https://codecov.io/gh/Davidelanz/quantum-robot/branch/master/graph/badge.svg?token=69IQEINMQU" />
    </a>
    <a href="#" alt="Development Status">
        <img src="https://pypip.in/status/quantum-robot/badge.svg" />
    </a>
    <a href="#" alt="Linux">
        <img src="https://img.shields.io/badge/linux-xenial | bionic-blue" />
    </a>
    <a href="#" alt="Python">
        <img src="https://img.shields.io/badge/python-3.6 | 3.7 | 3.8 -blue" />
    </a>
    <a href="https://pypi.org/project/quantum-robot/" alt="PyPi version">
        <img src="https://badge.fury.io/py/quantum-robot.svg" />
    </a>

</p>

<table align="center" style="width:80%; border: 1px solid black;">
    <tr>
    <th> <b>BEWARE:</b> package still under developement. If you are not one of the developers, it is not suggested to install it yet.
    </tr>
</table>
</p>

`quantum-robot` is a Python package for quantum-like perception modeling for robotics. The package exploits [Qiksit](https://qiskit.org/) framework, implementing the models on quantum circuits which can be simulated on a classical computer or sent to a quantum backend (service provided by [IBM Quantum Experience](https://quantum-computing.ibm.com/)). A [ROS](https://www.ros.org/) implementation is provided, in order to easily adapt the framework for real-time applications in robotics.

The project was started in 2019 by Davide Lanza as a Master thesis research, with the help of [Fulvio Mastrogiovanni](https://www.dibris.unige.it/mastrogiovanni-fulvio) and [Paolo Solinas](http://www.spin.cnr.it/index.php/people/46-researchers/49-solinas-paolo.html).

It is currently maintained by Davide Lanza.

Website: https://quantum-robot.org


## Summary

- [Installation](#installation)
<!--- [Development](#development)
- [Contributing](#contributing)
- [Credits](#credits)-->
- [License](#license)

## Installation[↑](#summary)

### Dependencies

[requirements.txt](https://github.com/Davidelanz/quantum-robot/blob/master/requirements.txt)

### User installation

The easiest way to install `quantum-robot` is using `pip`:
```
pip install -U quantum-robot
```

The package can be [installed from source](https://packaging.python.org/tutorials/installing-packages/#id19) as well. You can check the latest sources with the command:
```
git clone https://github.com/Davidelanz/quantum-robot.git
```

### Testing

After installation, you can launch the test suite from outside the source directory (you will need to have `pytest` installed):
```
pytest qrobot
```


## License[↑](#summary)

[GNU GPL](https://github.com/Davidelanz/quantum-robot/blob/master/LICENSE)
