FROM python:3.9

RUN add-apt-repository ppa:redislabs/redis -y \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends \
    # Install redis
    redis \
    # Clean up
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install quantum-robot via poetry
COPY ./src /src
RUN pipx install poetry && poetry install

# Start redis server
COPY ./docker/start_redis.sh /start_redis.sh
RUN chmod +x /start_redis.sh
ENTRYPOINT  [ "/start_redis.sh" ]

CMD [ "/bin/bash" ]