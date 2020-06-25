import setuptools

DISTNAME = 'quantum-robot'
VERSION = "0.0.1"
DESCRIPTION = 'A set of python modules for quantum-like perception modelling'
with open('README.rst') as f:
    LONG_DESCRIPTION = f.read()
AUTHOR = 'Davide Lanza'
AUTHOR_EMAIL = 'davidel96@hotmail.it'
MAINTAINER = 'Davide Lanza'
MAINTAINER_EMAIL = 'davidel96@hotmail.it'
URL = 'http://quantum-robot.org'
DOWNLOAD_URL = 'https://pypi.org/project/quantum-robot/#files'
LICENSE = 'GNU GPL'
PROJECT_URLS = {
    'Bug Tracker': 'https://github.com/Davidelanz/quantum-robot/issues',
    'Documentation': 'http://quantum-robot.org/docs',
    'Source Code': 'https://github.com/Davidelanz/quantum-robot'
}


setuptools.setup(
    name=DISTNAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer=MAINTAINER,
    maintainer_email=MAINTAINER_EMAIL,
    description=DESCRIPTION,
    license=LICENSE,
    url=URL,
    download_url=DOWNLOAD_URL,
    project_urls=PROJECT_URLS,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires='>=3.6',
    install_requires=[
        'pandas>=1.0.4'
        'numpy>=1.18.5'
        'qiskit>=0.19.3'
        'pytest>=5.4.3'
        'opencv-python>=4.2.0.34'
        'imutils>=0.5.3'
        'Matplotlib>=2.1.1'
    ],
)
