FROM ubuntu:focal

# Install software-properties-common
RUN apt-get update -y \
    && apt-get install software-properties-common -y --no-install-recommends\
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install python3
RUN add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update -y \
    && apt-get install python3.8 python3-pip -y --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install quantum-robot
WORKDIR /quantum-robot
COPY . /quantum-robot
RUN pip install --no-cache-dir /quantum-robot

CMD [ "/bin/bash" ]