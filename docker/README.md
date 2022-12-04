# Docker

## DockerHub images


A self-contained command-line interface is provided in the `Dockerfile` file.

To build the image:
```sh
cd quantum-robot/docker
docker build -t davidelanz/quantum-robot .
```

To run it:
```sh
docker run davidelanz/quantum-robot
```