# Docker

## DockerHub images

(...)

## Build the images yourself

### Multi-image ecosystem

 (...) Basic image used on docker-compose.yml (...)


### Self-contained image

A self-contained command-line interface is provided in the `Dockerfile_with_redis` file.
You can set up the container with:
```sh
cd quantum-robot
docker build -f docker/Dockerfile_with_redis -t davidelanz/quantum-robot:with_redis .
```

Now you can run it interactively (use the `exit` command to terminate the interactive session):
```sh
docker run -ti --rm davidelanz/quantum-robot:with_redis
```

You can your image to run local scripts as well. For example, for the `/path/to/script.py` file:
```sh
docker run -ti --rm -v /path/to/script.py:/run.py davidelanz/quantum-robot:with_redis python3 /run.py
```